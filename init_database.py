#!/usr/bin/env python3
"""
Database initialization script for NEXXT_AI_PROJECT.

This script initializes all database tables and populates them with initial data:
- Creates users table
- Creates products table
- Populates products from markdown files in products/ directory

Usage:
    python init_database.py
"""

from src.utils.db import init_database

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        exit(1)
