"""Simple Postgres helper for app (Streamlit) to store users from Register.

Uses psycopg (v3) and environment variables for configuration:
APP_DB_HOST, APP_DB_PORT, APP_DB_USER, APP_DB_PASSWORD, APP_DB_NAME, APP_DB_SSLMODE

Schema: 
- `users` table with core columns and an `extra` JSONB column
- `products` table for banking products from markdown files
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import psycopg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


KNOWN_COLUMNS = {
    "email",
    "password_hash",
    "first_name",
    "last_name",
    "age",
    "marital_status",
    "employment_status",
    "has_children",
    "number_of_children",
    "user_plan",
}


def _conn() -> psycopg.Connection:
    dsn = psycopg.conninfo.make_conninfo(
        host=os.getenv("APP_DB_HOST", os.getenv("PGHOST", "localhost")),
        port=os.getenv("APP_DB_PORT", os.getenv("PGPORT", "5432")),
        user=os.getenv("APP_DB_USER", os.getenv("PGUSER")),
        password=os.getenv("APP_DB_PASSWORD", os.getenv("PGPASSWORD")),
        dbname=os.getenv("APP_DB_NAME", os.getenv("PGDATABASE")),
        sslmode=os.getenv("APP_DB_SSLMODE", os.getenv("PGSSLMODE")),
    )
    return psycopg.connect(dsn, autocommit=True)


def init_users_table() -> None:
    """Create users table if missing (flexible schema with JSONB extras)."""
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        age INT,
        marital_status TEXT,
        employment_status TEXT,
        has_children BOOLEAN,
        number_of_children INT,
        user_plan TEXT,
        extra JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def init_products_table() -> None:
    """Create products table if missing."""
    sql = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        product_name TEXT UNIQUE NOT NULL,
        product_description TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS products_name_idx ON products (product_name);
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def upsert_user(data: Dict[str, Any]) -> None:
    """Insert or update a user by email. Extra keys go into `extra` JSONB.

    Required keys: email, password_hash
    """
    email = data.get("email")
    pwd = data.get("password_hash")
    if not email or not pwd:
        raise ValueError("email and password_hash are required")

    core = {k: data.get(k) for k in KNOWN_COLUMNS if k in data}
    extra = {k: v for k, v in data.items() if k not in KNOWN_COLUMNS}

    # Ensure types for booleans/ints are respected where possible
    if "has_children" in core and core["has_children"] is not None:
        core["has_children"] = bool(core["has_children"])
    if "number_of_children" in core and core["number_of_children"] is not None:
        try:
            core["number_of_children"] = int(core["number_of_children"])
        except Exception:
            core["number_of_children"] = None

    # Build columns dynamically
    columns = ["email", "password_hash"] + [c for c in KNOWN_COLUMNS if c not in {"email", "password_hash"}]
    payload = {
        "email": email,
        "password_hash": pwd,
        **{k: core.get(k) for k in columns if k not in {"email", "password_hash"}},
    }

    set_cols = ", ".join([f"{c} = EXCLUDED.{c}" for c in columns if c not in {"email"}])

    sql = f"""
    INSERT INTO users ({', '.join(columns)}, extra)
    VALUES ({', '.join(['%s'] * len(columns))}, %s::jsonb)
    ON CONFLICT (email) DO UPDATE SET
        {set_cols},
        extra = users.extra || EXCLUDED.extra,
        updated_at = now();
    """

    values = [payload[c] for c in columns]
    values.append(json.dumps(extra, ensure_ascii=False))

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, values)


def get_user_by_email(email: str) -> Dict[str, Any] | None:
    """Retrieve user by email from database.
    
    Returns a dict with user data including password_hash, or None if not found.
    """
    if not email:
        return None
    
    sql = """
    SELECT email, password_hash, first_name, last_name, age, 
           marital_status, employment_status, has_children, 
           number_of_children, user_plan, extra
    FROM users
    WHERE email = %s
    LIMIT 1;
    """
    
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (email,))
                row = cur.fetchone()
                
                if row is None:
                    return None
                
                # Map row to dictionary
                return {
                    "email": row[0],
                    "password_hash": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "age": row[4],
                    "marital_status": row[5],
                    "employment_status": row[6],
                    "has_children": row[7],
                    "number_of_children": row[8],
                    "user_plan": row[9],
                    "extra": row[10] if row[10] else {},
                }
    except Exception:
        # If database is not configured or connection fails, return None
        return None


def save_financial_plan(email: str, plan_text: str) -> bool:
    """
    Save or update the financial plan for a user.
    
    Args:
        email: User's email address
        plan_text: The markdown text of the financial plan
        
    Returns:
        True if successful, False otherwise
    """
    sql = """
    UPDATE users
    SET user_plan = %s,
        updated_at = now()
    WHERE email = %s;
    """
    
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (plan_text, email))
                conn.commit()
                return cur.rowcount > 0
    except Exception as e:
        print(f"Error saving financial plan: {e}")
        return False


def populate_products(products_dir: str | None = None) -> int:
    """
    Populate products table from markdown files in products directory.
    
    Args:
        products_dir: Path to products directory. If None, uses default '../products'
        
    Returns:
        Number of products inserted/updated
    """
    if products_dir is None:
        # Get the directory relative to this file
        current_file = Path(__file__)
        products_dir = current_file.parent.parent.parent / "products"
    else:
        products_dir = Path(products_dir)
    
    if not products_dir.exists():
        print(f"Products directory not found: {products_dir}")
        return 0
    
    # Find all .md files
    md_files = list(products_dir.glob("*.md"))
    
    if not md_files:
        print(f"No markdown files found in {products_dir}")
        return 0
    
    count = 0
    sql = """
    INSERT INTO products (product_name, product_description)
    VALUES (%s, %s)
    ON CONFLICT (product_name) DO UPDATE SET
        product_description = EXCLUDED.product_description,
        updated_at = now();
    """
    
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                for md_file in md_files:
                    # Use filename without extension as product_name
                    product_name = md_file.stem
                    
                    # Read file content as product_description
                    try:
                        product_description = md_file.read_text(encoding='utf-8')
                        cur.execute(sql, (product_name, product_description))
                        count += 1
                        print(f"✓ Inserted/Updated: {product_name}")
                    except Exception as e:
                        print(f"✗ Error reading {md_file.name}: {e}")
                        continue
                
                conn.commit()
    except Exception as e:
        print(f"Error populating products: {e}")
        return 0
    
    return count


def get_all_products() -> List[Dict[str, Any]]:
    """
    Retrieve all products from database.
    
    Returns:
        List of dictionaries with product data
    """
    sql = """
    SELECT id, product_name, product_description, created_at, updated_at
    FROM products
    ORDER BY product_name;
    """
    
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "product_name": row[1],
                        "product_description": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                    for row in rows
                ]
    except Exception as e:
        print(f"Error retrieving products: {e}")
        return []


def get_product_by_name(product_name: str) -> Dict[str, Any] | None:
    """
    Retrieve a specific product by name.
    
    Args:
        product_name: Name of the product
        
    Returns:
        Dictionary with product data or None if not found
    """
    sql = """
    SELECT id, product_name, product_description, created_at, updated_at
    FROM products
    WHERE product_name = %s
    LIMIT 1;
    """
    
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (product_name,))
                row = cur.fetchone()
                
                if row is None:
                    return None
                
                return {
                    "id": row[0],
                    "product_name": row[1],
                    "product_description": row[2],
                    "created_at": row[3],
                    "updated_at": row[4],
                }
    except Exception as e:
        print(f"Error retrieving product: {e}")
        return None


def init_database() -> None:
    """
    Initialize all database tables and populate products.
    Call this function to set up the entire database schema.
    """
    print("Initializing database...")
    
    # Create tables
    print("Creating users table...")
    init_users_table()
    
    print("Creating products table...")
    init_products_table()
    
    # Populate products
    print("Populating products from markdown files...")
    count = populate_products()
    
    print(f"\n✓ Database initialized successfully!")
    print(f"  - Users table: ready")
    print(f"  - Products table: {count} products loaded")

