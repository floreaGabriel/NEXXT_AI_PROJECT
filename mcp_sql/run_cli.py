#!/usr/bin/env python3
"""
Script pentru rularea CLI-ului MCP Agent
"""
import sys
import os

# Adaugă directorul părinte la path pentru importuri
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cli import main

if __name__ == "__main__":
    main()
