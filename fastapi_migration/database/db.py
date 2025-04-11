"""
Database utility module for working with SQLAlchemy and the GCP connection.

This module provides functions for:
1. Getting a database engine (using the same connection logic as the FastAPI app)
2. Performing database operations
3. Managing sessions

When integrating with the FastAPI backend, this will use the same
connection mechanism from app.db.session.
"""

import os
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    load_dotenv(env_file)
    logging.info(f"Loaded environment variables from {env_file}")

# For standalone use before integration
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

logger = logging.getLogger(__name__)

# This will be replaced with the actual function from app.db.session
def get_db_engine():
    """
    Returns a SQLAlchemy engine using the same connection logic as the FastAPI app.
    
    When integrated with the FastAPI codebase, this will use app.db.session.get_db_engine.
    For now, this is a placeholder implementation.
    """
    # Check for GCP database connection
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    instance_connection = os.getenv("INSTANCE_CONNECTION_NAME")
    
    if all([db_user, db_pass, db_name, instance_connection]):
        # Google Cloud SQL connection
        logger.info(f"Connecting to Google Cloud SQL instance: {instance_connection}")
        
        # This will use the Cloud SQL Python Connector with the connection string
        database_url = f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock=/cloudsql/{instance_connection}/.s.PGSQL.5432"
    else:
        # Simple direct connection for development
        database_url = os.getenv("DATABASE_URL", "postgresql://localhost/zando")
        
    logger.info(f"Using database connection with URL: {database_url}")
    
    # We'll use similar connection pooling parameters as the FastAPI implementation
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True
    )
    
    logger.info(f"Created database engine")
    return engine

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_session() as session:
            session.query(Model).all()
    """
    engine = get_db_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def init_models():
    """
    Initialize database tables based on SQLAlchemy models.
    
    This creates all tables defined in the models if they don't exist.
    """
    engine = get_db_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    return True