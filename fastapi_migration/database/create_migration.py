#!/usr/bin/env python
"""
Create the initial migration script based on the SQLAlchemy models.

Usage:
  python create_migration.py
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_initial_migration():
    """Create the initial migration script."""
    try:
        # Make sure we're in the correct directory
        migrations_dir = Path(__file__).parent / 'migrations'
        os.chdir(migrations_dir)
        
        # Check if versions directory exists
        if not Path('versions').exists():
            os.makedirs('versions')
            logger.info("Created versions directory")

        # Run alembic revision --autogenerate
        logger.info("Running alembic revision --autogenerate")
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial schema"], 
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.info(f"Created initial migration")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create migration: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error during migration creation: {str(e)}")
        return False

def main():
    """Main function."""
    logger.info("Starting migration creation")
    
    if not create_initial_migration():
        logger.error("Migration creation failed")
        sys.exit(1)
    
    logger.info("Initial migration creation completed successfully")
    logger.info("You can now run 'cd migrations && alembic upgrade head' to apply the migration")

if __name__ == "__main__":
    main()