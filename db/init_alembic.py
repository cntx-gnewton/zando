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

def create_initial_migration():
    """Create the initial migration script."""
    try:
        # Make sure we're in the migrations directory
        os.chdir(Path(__file__).parent / 'migrations')
        
        # Check if versions directory exists
        if not Path('versions').exists():
            os.makedirs('versions')
            logger.info("Created versions directory")

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
    except Exception as e:
        logger.error(f"Error during migration creation: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Initialize Alembic and create the first migration")
    args = parser.parse_args()
    
    if not create_initial_migration():
        sys.exit(1)
    
    logger.info("Initial migration creation completed successfully")
    logger.info("You can now run 'alembic upgrade head' to apply the migration")

if __name__ == "__main__":
    main()