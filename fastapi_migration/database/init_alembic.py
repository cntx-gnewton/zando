#!/usr/bin/env python
"""
Initialize Alembic and create the first migration.

This script sets up Alembic and creates the initial migration script
based on the SQLAlchemy models.

Usage:
  python init_alembic.py
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_alembic():
    """Set up Alembic for migration management."""
    try:
        # Check if Alembic is installed
        subprocess.run(["alembic", "--version"], check=True, capture_output=True)
        logger.info("Alembic is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Alembic is not installed. Please run 'pip install alembic'")
        return False
    
    # Set up migrations directory
    migrations_dir = Path("migrations")
    if not migrations_dir.exists():
        logger.info("Creating migrations directory structure")
        os.makedirs(migrations_dir / "versions", exist_ok=True)
        
    # Check if alembic.ini exists
    if not Path("migrations/alembic.ini").exists():
        logger.error("alembic.ini not found. Please run 'alembic init migrations' first")
        return False
        
    return True

def create_initial_migration():
    """Create the initial migration script."""
    try:
        # Run alembic revision --autogenerate
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial schema"], 
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Created initial migration: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create migration: {e.stderr}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Initialize Alembic and create the first migration")
    args = parser.parse_args()
    
    if not setup_alembic():
        sys.exit(1)
    
    if not create_initial_migration():
        sys.exit(1)
    
    logger.info("Alembic setup and initial migration creation completed successfully")
    logger.info("You can now run 'alembic upgrade head' to apply the migration")

if __name__ == "__main__":
    main()