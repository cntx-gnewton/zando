#!/usr/bin/env python3
"""
Simple wrapper script to run the migration tool.
This script is a convenience wrapper around the db_migrations module.
"""

import sys
import os

# Add the parent directory to the path so we can import db_migrations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from cli.py
try:
    from db_migrations.cli import main
except ModuleNotFoundError:
    # Try loading from current directory
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_migrations"))
    from cli import main

if __name__ == "__main__":
    main()