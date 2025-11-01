#!/usr/bin/env python3
"""Migration script to add user_plan column to existing users table."""

import os
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_connection():
    """Create database connection."""
    dsn = psycopg.conninfo.make_conninfo(
        host=os.getenv("APP_DB_HOST", os.getenv("PGHOST", "localhost")),
        port=os.getenv("APP_DB_PORT", os.getenv("PGPORT", "5432")),
        user=os.getenv("APP_DB_USER", os.getenv("PGUSER")),
        password=os.getenv("APP_DB_PASSWORD", os.getenv("PGPASSWORD")),
        dbname=os.getenv("APP_DB_NAME", os.getenv("PGDATABASE")),
        sslmode=os.getenv("APP_DB_SSLMODE", os.getenv("PGSSLMODE")),
    )
    return psycopg.connect(dsn)


def migrate():
    """Add user_plan column to users table if it doesn't exist."""
    
    print("🔄 Starting migration: Add user_plan column...")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if column already exists
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'user_plan';
                """)
                
                column_exists = cur.fetchone()
                
                if column_exists:
                    print("✅ Column 'user_plan' already exists. Nothing to do.")
                    return
                
                # Add the column
                print("📝 Adding 'user_plan' column to 'users' table...")
                cur.execute("""
                    ALTER TABLE users 
                    ADD COLUMN user_plan TEXT;
                """)
                
                conn.commit()
                print("✅ Migration successful! Column 'user_plan' added to 'users' table.")
                
                # Verify the column was added
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'user_plan';
                """)
                result = cur.fetchone()
                
                if result:
                    print(f"✅ Verification: Column '{result[0]}' with type '{result[1]}' exists.")
                else:
                    print("⚠️ Warning: Could not verify column creation.")
                    
    except psycopg.Error as e:
        print(f"❌ Database error during migration: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        raise


if __name__ == "__main__":
    migrate()
