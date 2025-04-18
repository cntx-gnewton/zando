#!/usr/bin/env python3
import os
import glob
import logging
import sys
import argparse
import sqlalchemy

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import the database connection module
from db_connection import (
    load_config, 
    get_db_connection, 
    execute_sql_script_file
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_functions(env='development'):
    """Apply database functions."""
    config = load_config(env)
    conn = get_db_connection(config, env)
    
    try:
        # Update migration status if needed
        version = '0004_database_functions'
        description = 'database_functions'
        
        # Get functions directory
        functions_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'migrations/0004_database_functions/functions'
        )
        
        # Apply each function file individually
        function_files = glob.glob(os.path.join(functions_dir, '*.sql'))
        function_files.sort()  # Sort to ensure correct order
        
        for function_file in function_files:
            file_name = os.path.basename(function_file)
            logger.info(f"Applying function file: {file_name}")
            
            try:
                # Create individual transactions for each function file
                conn.begin()
                execute_sql_script_file(conn, function_file)
                conn.commit()
                logger.info(f"Successfully applied: {file_name}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Error applying {file_name}: {e}")
                
        # Mark the migration as applied if not already
        conn.begin()
        check_query = "SELECT 1 FROM schema_migrations WHERE version = :version"
        result = conn.execute(sqlalchemy.text(check_query), {"version": version})
        exists = bool(result.fetchone())
        
        if not exists:
            query = "INSERT INTO schema_migrations (version, description) VALUES (:version, :description)"
            conn.execute(sqlalchemy.text(query), {"version": version, "description": description})
            conn.commit()
            logger.info(f"Migration {version} marked as applied")
        else:
            logger.info(f"Migration {version} was already marked as applied")

    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply database functions')
    parser.add_argument('--env', default='development', help='Environment to use')
    args = parser.parse_args()
    
    apply_functions(args.env)