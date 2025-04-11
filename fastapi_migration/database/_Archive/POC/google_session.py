import os
import logging
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    from google.cloud.sql.connector import Connector, IPTypes
    import pg8000
except ImportError:
    logging.warning("Google Cloud SQL connector not installed. Using direct database connection.")
    Connector = None
    IPTypes = None
    pg8000 = None

from project_settings import Settings
settings = Settings()
# Set up logging
logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global engine for connection pooling
_engine = None

def get_db_engine() -> sqlalchemy.engine.base.Engine:
    """
    Returns a global SQLAlchemy engine instance with connection pooling.
    
    This creates a singleton engine that can be reused across requests,
    improving performance by avoiding repeated connection establishment.
    
    Returns:
        SQLAlchemy engine with connection pooling
    """
    global _engine
    
    if _engine is not None:
        # Return existing engine if already created
        return _engine
    
    # Check if we're running in GCP environment
    if Connector and os.environ.get("INSTANCE_CONNECTION_NAME"):
        # Create Cloud SQL connection using the connector
        instance_connection_name = settings.INSTANCE_CONNECTION_NAME
        db_user = settings.DB_USER
        db_pass = settings.DB_PASS
        db_name = settings.DB_NAME
        # db_user = os.environ.get("DB_USER", settings.DB_USER)
        # db_pass = os.environ.get("DB_PASS", settings.DB_PASS)
        # db_name = os.environ.get("DB_NAME", settings.DB_NAME)
        
        ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
        
        connector = Connector(refresh_strategy="LAZY")
        
        def getconn() -> pg8000.dbapi.Connection:
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
        
        logger.info("Google Cloud SQL connection pool initialized")
    else:
        # Use direct database connection for local development
        _engine = sqlalchemy.create_engine(
            settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
        
        logger.info("Direct database connection pool initialized")
    
    return _engine

# Create session factory for synchronous operations
engine = get_db_engine()
SyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# For compatibility with existing async code, we'll create a simple async session factory
# NOTE: This is a workaround for the transition - it uses sync engine under the hood
class SimpleAsyncSession(AsyncSession):
    """
    A simplified AsyncSession that wraps a synchronous session for compatibility.
    This allows us to maintain the async interface while using the synchronous Google Cloud SQL connector.
    """
    # Store the session as an instance attribute to keep it alive through method calls
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sync_session = None
        
    def _get_session(self):
        """Get or create a sync session."""
        if self._sync_session is None:
            self._sync_session = SyncSessionLocal()
        return self._sync_session
    
    async def execute(self, statement, params=None, **kwargs):
        """Execute a statement and return a buffered result."""
        # Use a persistent session to avoid context issues
        session = self._get_session()
        result = session.execute(statement, params, **kwargs)
        return result
    
    async def commit(self):
        """Commit the current transaction."""
        if self._sync_session:
            self._sync_session.commit()
    
    async def rollback(self):
        """Rollback the current transaction."""
        if self._sync_session:
            self._sync_session.rollback()
    
    async def close(self):
        """Close the session."""
        if self._sync_session:
            self._sync_session.close()
            self._sync_session = None
            
    async def connection(self):
        """Return a connection object."""
        # This is a simplification - it returns the session itself as a connection proxy
        return self
    
    async def refresh(self, instance, **kwargs):
        """Refresh the attributes of the given instance."""
        session = self._get_session()
        session.refresh(instance, **kwargs)

# Create async session factory (simplified for transition)
SessionLocal = sessionmaker(
    class_=SimpleAsyncSession,
    expire_on_commit=False
)

# Utility function to initialize database
async def init_db():
    """
    Initialize database - create tables if they don't exist.
    Called during application startup.
    """
    try:
        # Use a synchronous operation wrapped in an async function
        with engine.begin() as conn:
            # Create all tables
            Base.metadata.create_all(bind=conn)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False