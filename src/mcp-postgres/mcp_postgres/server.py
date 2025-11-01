"""MCP Postgres Server (SSE transport)

Provides read-only SQL access to a PostgreSQL database via the Model Context
Protocol (MCP). Exposes tools for querying data and inspecting schema.

Transport: SSE over HTTP (Starlette + uvicorn).

Environment variables:
  - PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE, PGSSLMODE (optional)
  - READ_ONLY: "true" (default) prevents non-SELECT statements
  - QUERY_ROW_LIMIT: default 200 (max rows returned by tools unless overridden)
  - SERVER_HOST: default 0.0.0.0
    - SERVER_PORT: default 8042

Endpoints (via SseServer.register_routes):
  - /mcp: SSE endpoint for MCP clients

Tools:
  - health(): basic health check
  - sql_schema(include_views: bool = True): database schema overview
  - table_sample(table: str, limit: int = 20): preview data from a table
  - sql_query(sql: str, params: dict | None = None, limit: int | None = None, timeout: int | None = None)

NOTE: This server is intended for read-only use by LLM agents.
"""

from __future__ import annotations

import json
import os
import re
import typing as t

import psycopg
from pydantic import BaseModel
from starlette.applications import Starlette
import uvicorn

from mcp.server import Server
from mcp.server.sse import SseServer


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

READ_ONLY = os.getenv("READ_ONLY", "true").lower() in {"1", "true", "yes"}
DEFAULT_ROW_LIMIT = int(os.getenv("QUERY_ROW_LIMIT", "200"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8042"))


def _get_conn() -> psycopg.Connection:
    dsn = psycopg.conninfo.make_conninfo(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        dbname=os.getenv("PGDATABASE"),
        sslmode=os.getenv("PGSSLMODE"),
    )
    return psycopg.connect(dsn, autocommit=True)


def _enforce_read_only(sql: str) -> None:
    if not READ_ONLY:
        return
    # Allow only SELECT, WITH (leading CTEs for SELECT), and EXPLAIN SELECT
    normalized = sql.strip().lower()
    # Quick reject for mutating keywords
    forbidden = [
        "insert", "update", "delete", "drop", "alter", "create", "truncate",
        "grant", "revoke", "comment", "vacuum", "analyze", "refresh materialized view",
    ]
    if any(re.search(rf"\b{kw}\b", normalized) for kw in forbidden):
        raise ValueError("READ_ONLY is enabled: only SELECT-like queries are permitted")
    # Must start with select-like
    if not (normalized.startswith("select") or normalized.startswith("with") or normalized.startswith("explain select")):
        raise ValueError("Only SELECT / WITH (select) / EXPLAIN SELECT queries are allowed in READ_ONLY mode")


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[list[t.Any]]
    row_count: int
    truncated: bool


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

server = Server("mcp-postgres")


@server.tool()
def health() -> str:
    """Basic health check and connection test."""
    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                _ = cur.fetchone()
        return "ok"
    except Exception as e:
        return f"error: {e}"


@server.tool()
def sql_schema(include_views: bool = True) -> str:
    """Return a simple schema overview (tables, columns, types)."""
    query = (
        """
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position
        """
    )
    if not include_views:
        query = (
            """
            SELECT c.table_schema, c.table_name, c.column_name, c.data_type
            FROM information_schema.columns c
            JOIN information_schema.tables t
              ON t.table_schema = c.table_schema AND t.table_name = c.table_name
            WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
              AND t.table_type = 'BASE TABLE'
            ORDER BY c.table_schema, c.table_name, c.ordinal_position
            """
        )

    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    by_table: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for schema, table, col, dtype in rows:
        by_table.setdefault((schema, table), []).append((col, dtype))

    lines: list[str] = []
    for (schema, table), cols in by_table.items():
        lines.append(f"{schema}.{table}")
        for col, dtype in cols:
            lines.append(f"  - {col}: {dtype}")
    return "\n".join(lines)


@server.tool()
def table_sample(table: str, limit: int = 20) -> str:
    """Return a small sample of rows for a given table (as JSON text)."""
    _enforce_read_only("select 1")
    if limit <= 0:
        limit = 20
    from psycopg import sql as psql
    with _get_conn() as conn:
        with conn.cursor() as cur:
            query = psql.SQL("SELECT * FROM {} LIMIT %s").format(psql.Identifier(table))
            cur.execute(query, (limit,))
            cols = [desc[0] for desc in cur.description]
            data = cur.fetchall()
    as_dicts = [dict(zip(cols, row)) for row in data]
    return json.dumps({"columns": cols, "rows": as_dicts}, ensure_ascii=False)


@server.tool()
def sql_query(
    sql: str,
    params: dict | None = None,
    limit: int | None = None,
    timeout: int | None = None,
) -> str:
    """Execute a read-only SQL query and return rows as JSON.

    - sql: SELECT/EXPLAIN/CTE SELECT query
    - params: optional mapping for %s placeholders
    - limit: max rows to return (defaults to QUERY_ROW_LIMIT)
    - timeout: statement timeout in milliseconds
    """
    _enforce_read_only(sql)
    max_rows = limit or DEFAULT_ROW_LIMIT
    if max_rows <= 0:
        max_rows = DEFAULT_ROW_LIMIT

    with _get_conn() as conn:
        if timeout and timeout > 0:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = %s", (timeout,))
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params.values()) if params else None)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows: list[list[t.Any]] = []
            truncated = False
            count = 0
            while True:
                batch = cur.fetchmany(size=100)
                if not batch:
                    break
                for r in batch:
                    if count < max_rows:
                        rows.append(list(r))
                    count += 1
                    if count >= max_rows:
                        truncated = True
                        # Consume remaining cursor results without storing (optional)
                        continue

    result = QueryResult(columns=columns, rows=rows, row_count=count, truncated=truncated)
    return result.model_dump_json()


# ---------------------------------------------------------------------------
# Starlette app (no auth)
# ---------------------------------------------------------------------------
app = Starlette()
sse = SseServer(server)
sse.register_routes(app)


def main() -> None:
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)


if __name__ == "__main__":
    main()
