#!/usr/bin/env python3
import argparse
import logging
from migrations import SqlMigrationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migrate")

def main():
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument('--direction', choices=['up', 'down'], default='up',
                      help='Migration direction (up or down)')
    parser.add_argument('--component', choices=['all', 'tables', 'functions', 'types', 'sequences', 'views', 'config'],
                      default='all', help='Component type to migrate')
    parser.add_argument('--version', help='Target version to migrate to')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--file', help='Execute a specific SQL file')
    parser.add_argument('--dir', help='Execute all SQL files in a directory')
    # Removed history-related arguments as we no longer track migrations
    
    args = parser.parse_args()
    
    manager = SqlMigrationManager(config_path=args.config)
    
    # Removed history display code as we no longer track migrations
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