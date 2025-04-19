import os
import logging
import sqlalchemy
from sqlalchemy.orm import sessionmaker

try:
    from google.cloud.sql.connector import Connector, IPTypes
    import pg8000
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    logging.warning("Google Cloud SQL connector not installed. Using direct database connection.")
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

def create_db_engine(db_config):
    """
    Create a SQLAlchemy engine based on the provided configuration.
    
    Args:
        db_config: Dictionary containing database configuration
        
    Returns:
        SQLAlchemy engine
    """
    # Check if we should use Google Cloud SQL
    if GOOGLE_CLOUD_AVAILABLE and db_config.get('use_gcp', False):

        return _create_gcp_engine(db_config)
    else:
        # return _create_direct_engine(db_config)
        raise RuntimeError(f"Got unsupported database configuration: {db_config}")
        
def _create_gcp_engine(db_config):
    """
    Create a Google Cloud SQL connection engine.
    
    Args:
        db_config: Dictionary containing database configuration
        
    Returns:
        SQLAlchemy engine for Google Cloud SQL
    """
    instance_connection_name = db_config.get('instance_connection_name')
    db_user = db_config.get('user')
    db_pass = db_config.get('password')
    db_name = db_config.get('database')
    
    if not all([instance_connection_name, db_user, db_pass, db_name]):
        raise ValueError("Missing required GCP database configuration values")
    
    ip_type = IPTypes.PRIVATE if db_config.get('use_private_ip', False) else IPTypes.PUBLIC
    
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
    engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # Pool settings
        pool_size=5,               # Default number of connections to maintain
        max_overflow=10,           # Allow up to 10 additional connections on high load
        pool_timeout=30,           # Wait up to 30 seconds for a connection
        pool_recycle=1800,         # Recycle connections after 30 minutes
        pool_pre_ping=True         # Check connection viability before using
    )
    
    logger.info("Google Cloud SQL connection pool initialized")
    return engine
    
def _create_direct_engine(db_config):
    """
    Create a direct database connection engine.
    
    Args:
        db_config: Dictionary containing database configuration
        
    Returns:
        SQLAlchemy engine for direct database connection
    """
    # Check if a full connection string is provided
    if 'url' in db_config:
        connection_string = db_config['url']
    else:
        # Build connection string from components
        user = db_config.get('user', 'postgres')
        password = db_config.get('password', 'postgres')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        database = db_config.get('database', 'postgres')
        
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Create engine with connection pooling
    engine = sqlalchemy.create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
    
    logger.info("Direct database connection pool initialized")
    return engine
    
def create_session_factory(engine):
    """
    Create a session factory for the given engine.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        SQLAlchemy sessionmaker
    """
    return sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )