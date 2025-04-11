#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import yaml
from db_migrations.core.manager import SqlMigrationManager
from db_migrations.utils.db_session import create_db_engine, create_session_factory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("migrate")

def load_db_config(config_file=None, env="development"):
    """
    Load database configuration from file.
    
    Args:
        config_file: Path to configuration file
        env: Environment to use (development, production, etc.)
        
    Returns:
        Database configuration dictionary
    """
    # Default config paths to check
    config_paths = [
        config_file,
        os.path.join(os.getcwd(), "db_config.yaml"),
        os.path.join(os.getcwd(), "database", "db_config.yaml"),
        "/etc/zando/db_config.yaml"
    ]
    
    for path in config_paths:
        if path and os.path.exists(path):
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded database configuration from {path}")
                
                # Use specified environment or active_profile
                active_env = env or config.get('active_profile', 'development')
                if active_env in config:
                    return config[active_env]
                else:
                    logger.warning(f"Environment {active_env} not found in config, using first available")
                    # Get the first environment that's not 'active_profile'
                    for key in config:
                        if key != 'active_profile' and isinstance(config[key], dict):
                            return config[key]
    
    # Check environment variables if no config file found
    if all([os.environ.get(var) for var in ["DB_USER", "DB_PASS", "DB_NAME"]]):
        return {
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASS"),
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": int(os.environ.get("DB_PORT", 5432)),
            "database": os.environ.get("DB_NAME"),
            "use_gcp": os.environ.get("USE_GCP", "false").lower() == "true",
            "instance_connection_name": os.environ.get("INSTANCE_CONNECTION_NAME", "")
        }
        
    # Default configuration for local development
    logger.warning("No database configuration found, using default local development settings")
    return {
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "postgres"
    }

def main():
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument('--direction', choices=['up', 'down', 'populate'], default='up',
                      help='Migration direction (up, down, or populate data)')
    parser.add_argument('--env', choices=['development', 'production'], default='development',
                      help='Environment configuration to use')
    parser.add_argument('--component', choices=['all', 'tables', 'functions', 'types', 'sequences', 'views', 'config'],
                      default='all', help='Component type to migrate')
    parser.add_argument('--table', help='Specific table to populate (with --direction populate)')
    parser.add_argument('--version', help='Target version to migrate to')
    parser.add_argument('--config', help='Path to migration configuration file')
    parser.add_argument('--db-config', help='Path to database configuration file')
    parser.add_argument('--sql-dir', help='Directory containing SQL migration files')
    parser.add_argument('--data-dir', help='Directory containing data CSV files')
    parser.add_argument('--file', help='Execute a specific SQL file')
    parser.add_argument('--dir', help='Execute all SQL files in a directory')
    
    args = parser.parse_args()
    
    # Load database configuration
    db_config = load_db_config(args.db_config, args.env)
    
    # Create database engine and session factory
    engine = create_db_engine(db_config)
    session_factory = create_session_factory(engine)
    
    # Create migration manager
    manager = SqlMigrationManager(
        db_session=session_factory,
        config_path=args.config,
        sql_dir=args.sql_dir,
        data_dir=args.data_dir
    )
    
    # Execute requested operation
    if args.dir:
        # Apply all SQL files in a directory
        success = manager.apply_directory_migrations(args.dir)
        if success:
            logger.info(f"Successfully applied all migrations in directory: {args.dir}")
        else:
            logger.error(f"Failed to apply migrations in directory: {args.dir}")
            exit(1)
    elif args.file:
        # Apply specific migration file
        success = manager.apply_specific_migration(args.component, args.file)
        if success:
            logger.info(f"Successfully applied migration file: {args.file}")
        else:
            logger.error(f"Failed to apply migration file: {args.file}")
            exit(1)
    elif args.direction == 'populate':
        # Populate data from CSV files
        success = manager.populate_data(args.table)
        if success:
            if args.table:
                logger.info(f"Successfully populated table: {args.table}")
            else:
                logger.info("Successfully populated all tables")
        else:
            if args.table:
                logger.error(f"Failed to populate table: {args.table}")
            else:
                logger.error("Failed to populate tables")
            exit(1)
    elif args.direction == 'up':
        # Apply migrations
        success = manager.migrate_up(args.component, args.version)
        if success:
            logger.info(f"Successfully applied migrations for {args.component or 'all'} components")
        else:
            logger.error(f"Failed to apply migrations for {args.component or 'all'} components")
            exit(1)
    else:
        # Roll back migrations
        success = manager.migrate_down(args.component, args.version)
        if success:
            logger.info(f"Successfully rolled back migrations for {args.component or 'all'} components")
        else:
            logger.error(f"Failed to roll back migrations for {args.component or 'all'} components")
            exit(1)

if __name__ == '__main__':
    main()