# MCP Postgres Server (SSE)

Read-only Model Context Protocol server exposing PostgreSQL via SSE/HTTP.

- Transport: SSE over HTTP (Starlette + uvicorn)
- Auth: none (no token required)
- Tools: `health`, `sql_schema`, `table_sample`, `sql_query`
- Safe by default: `READ_ONLY=true` allows only SELECT/CTE/EXPLAIN SELECT

## Quick start

1) Copy env and edit connection values:

```bash
cp .env.example .env
```

2) Build and run with Docker Compose:

```bash
docker compose --env-file .env up --build -d
```

Server will listen on http://localhost:8042/mcp

## Environment variables

- PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE, PGSSLMODE
- READ_ONLY (default: true)
- QUERY_ROW_LIMIT (default: 200)

## Tools

- health() -> str
  - Simple connectivity check.

- sql_schema(include_views: bool = True) -> str
  - Lists tables/columns in non-system schemas.

- table_sample(table: str, limit: int = 20) -> str (JSON)
  - Returns `{ columns: string[], rows: object[] }` sample rows.

- sql_query(sql: str, params: dict | None = None, limit: int | None = None, timeout: int | None = None) -> str (JSON)
  - Executes a read-only query.
  - Returns `{ columns: string[], rows: any[][], row_count: number, truncated: boolean }`.

## Client usage (MCP SSE)

Python (mcp client) example:

```python
import asyncio
from mcp.client.sse import sse_connect
from mcp.client.session import ClientSession

async def main():
    async with sse_connect("http://localhost:8042/mcp") as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # List tools
            tools = await session.list_tools()
            print(tools)

            # Call schema tool
            result = await session.call_tool("sql_schema", {"include_views": True})
            print(result)

            # Query example
            res = await session.call_tool("sql_query", {"sql": "SELECT now()"})
            print(res)

asyncio.run(main())
```

## Integration with Agents

- This service provides data access as an MCP server. Most LLM agent frameworks that support MCP can attach this server via SSE endpoint and call the `sql_*` tools.
- Keep `READ_ONLY=true` in production; if you need write access, change at your own risk.

## Notes

- Container uses `psycopg[binary]` for simplicity.
- If you need SSL, set `PGSSLMODE=require` and ensure your Postgres accepts TLS.
