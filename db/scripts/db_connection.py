#!/usr/bin/env python3
import os
import logging
import sqlalchemy
from dotenv import load_dotenv
import yaml
from pathlib import Path

# Try to import Google Cloud SQL connector
try:
    from google.cloud.sql.connector import Connector, IPTypes
    import pg8000
    HAVE_CLOUD_SQL = True
except ImportError:
    logging.warning("Google Cloud SQL connector not installed. Using direct database connection.")
    HAVE_CLOUD_SQL = False
    Connector = None
    IPTypes = None
    pg8000 = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Global engine for connection pooling
_engine = None

def load_config(env='development'):
    """Load configuration for specified environment."""
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
        return config.get(env, config.get('development'))

def get_db_engine(config=None, env='development'):
    """
    Returns a global SQLAlchemy engine instance with connection pooling.
    
    This creates a singleton engine that can be reused across requests,
    improving performance by avoiding repeated connection establishment.
    
    Args:
        config: Configuration dictionary (optional)
        env: Environment name to load configuration from
        
    Returns:
        SQLAlchemy engine with connection pooling
    """
    global _engine
    
    if _engine is not None:
        # Return existing engine if already created
        return _engine
    
    # Load config if not provided
    if config is None:
        config = load_config(env)
    
    # Check if we're using Google Cloud SQL
    if HAVE_CLOUD_SQL and 'instance_connection_name' in config and config['instance_connection_name']:
        # Create Cloud SQL connection using the connector - force config values
        instance_connection_name = config['instance_connection_name']
        db_user = config['user']
        db_pass = config['password']
        db_name = config['database']
        
        # Log the connection we're using for debugging
        logger.info(f"Using instance connection name: {instance_connection_name}")
        
        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
        
        connector = Connector(refresh_strategy="LAZY")
        
        def getconn():
            conn = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
                ip_type=ip_type,
            )
            return conn
        
        # Configure pooling parameters for better performance
        _engine = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            # Pool settings
            pool_size=5,               # Default number of connections to maintain
            max_overflow=10,           # Allow up to 10 additional connections on high load
            pool_timeout=30,           # Wait up to 30 seconds for a connection
            pool_recycle=1800,         # Recycle connections after 30 minutes
            pool_pre_ping=True         # Check connection viability before using
        )
        
        logger.info(f"Google Cloud SQL connection pool initialized for {instance_connection_name}")
    else:
        # Use direct database connection for local development
        db_url = (
            f"postgresql+psycopg2://"
            f"{config['user']}:"
            f"{config['password']}@"
            f"{config['host']}:"
            f"{config['port']}/"
            f"{config['database']}"
        )
        
        _engine = sqlalchemy.create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        logger.info(f"Direct database connection pool initialized to {config['host']}")
    
    return _engine

def get_db_connection(config=None, env='development'):
    """
    Get a database connection from the connection pool.
    
    Args:
        config: Configuration dictionary (optional)
        env: Environment name to load configuration from
        
    Returns:
        Database connection from the pool
    """
    engine = get_db_engine(config, env)
    return engine.connect()

def execute_sql_script(connection, script):
    """
    Execute a SQL script on the given connection.
    
    Args:
        connection: Database connection
        script: SQL script text to execute
        
    Returns:
        Result of execution
    """
    try:
        # First check if there's a transaction in progress
        in_transaction = False
        try:
            # Try to query something simple to check transaction status
            connection.execute(sqlalchemy.text("SELECT 1"))
            in_transaction = True
        except Exception:
            # If error, we might be between transactions or have other issues
            in_transaction = False
            
        # Execute the script - check if it's already a TextClause
        if isinstance(script, sqlalchemy.sql.elements.TextClause):
            return connection.execute(script)
        else:
            return connection.execute(sqlalchemy.text(script))
    except Exception as e:
        logger.error(f"Error executing SQL script: {e}")
        
        # Handle specific errors related to partial migrations
        if "already exists" in str(e):
            logger.warning("Ignoring 'already exists' error as it might be from a partial migration")
        else:
            raise

def execute_sql_script_file(connection, file_path):
    """
    Execute a SQL script file on the given connection.
    
    Args:
        connection: Database connection
        file_path: Path to SQL script file
        
    Returns:
        Result of execution
    """
    with open(file_path, 'r') as f:
        script = f.read()
    
    return execute_sql_script(connection, script)

def load_csv_to_db(engine, table_name, csv_path, columns=None):
    """
    Load data from a CSV file into a database table using SQLAlchemy COPY.
    
    Args:
        engine: SQLAlchemy engine
        table_name: Target table name
        csv_path: Path to CSV file
        columns: List of column names (optional)
        
    Returns:
        Number of rows loaded
    """
    import pandas as pd
    
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Filter columns if specified
    if columns:
        df = df[columns]
    
    # Load data to database
    with engine.begin() as conn:
        # Use pandas to_sql for efficient data loading
        row_count = df.to_sql(
            table_name, 
            conn, 
            if_exists='append', 
            index=False,
            method='multi',  # Batch inserts for better performance
            chunksize=1000   # Process in chunks to handle large files
        )
    
    logger.info(f"Loaded {row_count} rows into {table_name} from {csv_path}")
    return row_count