#!/usr/bin/env python3
import argparse
import os
import sys
import logging
import sqlalchemy

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import utility functions
from migrate import run_migrations
from db_connection import load_config, get_db_engine, get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(args):
    """Initialize the database from scratch."""
    config = load_config(args.env)
    
    # For Google Cloud SQL, we don't need to create the database
    if 'instance_connection_name' in config and config['instance_connection_name']:
        logger.info(f"Using Google Cloud SQL instance: {config['instance_connection_name']}")
        logger.info(f"Using database: {config['database']}")
        logger.info("Skipping database creation step (Cloud SQL databases must be created in the Google Cloud Console)")
        
        # Run all migrations
        run_migrations(args.env)
    else:
        # This is for local development
        try:
            import psycopg2  # Only needed for direct database creation
            
            # Connect to PostgreSQL server (not the specific database)
            admin_conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database='postgres',  # Connect to default database
                user=config['user'],
                password=config['password']
            )
            admin_conn.autocommit = True
        
            # Create database if it doesn't exist
            with admin_conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'")
                db_exists = cur.fetchone()
                
                if not db_exists:
                    logger.info(f"Creating database {config['database']}...")
                    cur.execute(f"CREATE DATABASE {config['database']}")
                    logger.info(f"Database {config['database']} created.")
                else:
                    logger.info(f"Database {config['database']} already exists.")
            
            admin_conn.close()
            
            # Run all migrations
            run_migrations(args.env)
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            sys.exit(1)

def reset_db(args):
    """Reset the database (drop and recreate)."""
    config = load_config(args.env)
    
    if args.env == 'production' and not args.force:
        logger.warning("Refusing to reset production database without --force flag.")
        return
    
    # For Google Cloud SQL, we warn that this isn't supported
    if 'instance_connection_name' in config and config['instance_connection_name']:
        logger.info(f"Using Google Cloud SQL instance: {config['instance_connection_name']}")
        logger.warning("WARNING: Full database reset isn't supported for Cloud SQL in this tool.")
        logger.info("Instead, we'll truncate all tables and rerun migrations.")
        
        try:
            # Connect to the database
            conn = get_db_connection(config, args.env)
            
            # Truncate all tables (except schema_migrations which will be handled by the migrations)
            tables_result = conn.execute(sqlalchemy.text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' AND tablename != 'schema_migrations'
            """))
            
            tables = [row[0] for row in tables_result]
            
            if tables:
                logger.info(f"Truncating {len(tables)} tables...")
                conn.execute(sqlalchemy.text(f"TRUNCATE TABLE {', '.join(tables)} CASCADE"))
                conn.commit()
                logger.info("Tables truncated.")
            else:
                logger.info("No tables found to truncate.")
            
            conn.close()
            
            # Run all migrations
            run_migrations(args.env)
            
        except Exception as e:
            logger.error(f"Error resetting tables: {e}")
            sys.exit(1)
    else:
        try:
            import psycopg2  # Only needed for direct database creation
            
            # Connect to PostgreSQL server (not the specific database)
            admin_conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database='postgres',  # Connect to default database
                user=config['user'],
                password=config['password']
            )
            admin_conn.autocommit = True
            
            # Drop database if it exists
            with admin_conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'")
                db_exists = cur.fetchone()
                
                if db_exists:
                    logger.info(f"Dropping database {config['database']}...")
                    
                    # Terminate all connections
                    cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{config['database']}'
                    AND pid <> pg_backend_pid()
                    """)
                    
                    cur.execute(f"DROP DATABASE {config['database']}")
                    logger.info(f"Database {config['database']} dropped.")
                
                # Create new database
                logger.info(f"Creating database {config['database']}...")
                cur.execute(f"CREATE DATABASE {config['database']}")
                logger.info(f"Database {config['database']} created.")
            
            admin_conn.close()
            
            # Run all migrations
            run_migrations(args.env)
            
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            sys.exit(1)

def check_db(args):
    """Check database connection and tables."""
    config = load_config(args.env)
    
    try:
        # Get a SQLAlchemy connection
        conn = get_db_connection(config, args.env)
        
        # Check if we can connect
        logger.info(f"Successfully connected to database {config['database']}.")
        if 'instance_connection_name' in config and config['instance_connection_name']:
            logger.info(f"Using Google Cloud SQL instance: {config['instance_connection_name']}")
        
        # Get list of tables
        result = conn.execute(sqlalchemy.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        
        if tables:
            logger.info(f"Found {len(tables)} tables:")
            for table in tables:
                # Get row count
                count_result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {table}"))
                row_count = count_result.scalar()
                logger.info(f"  - {table}: {row_count} rows")
        else:
            logger.info("No tables found in database.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument('--env', default='development',
                      help='Environment (development, test, production, cloud)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.set_defaults(func=init_db)
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database (drop and recreate)')
    reset_parser.add_argument('--force', action='store_true', help='Force reset in production')
    reset_parser.set_defaults(func=reset_db)
    
    # migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    migrate_parser.set_defaults(func=lambda args: run_migrations(args.env))
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check database connection and tables')
    check_parser.set_defaults(func=check_db)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)