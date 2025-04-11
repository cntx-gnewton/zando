"""
Database connection module for the Zando application.

This module provides functions for connecting to the database,
managing sessions, and initializing the database.
"""

import os
import logging
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    load_dotenv(env_file)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """
    Get the database URL from environment variables.
    
    Returns:
        str: Database URL
    """
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    server = os.getenv("POSTGRES_SERVER", "localhost")
    db = os.getenv("POSTGRES_DB", "zando")
    
    return f"postgresql://{user}:{password}@{server}/{db}"

def get_engine(database_url: str = None):
    """
    Get a SQLAlchemy engine.
    
    Args:
        database_url (str, optional): Database URL. If not provided, will use environment variables.
    
    Returns:
        Engine: SQLAlchemy engine
    """
    if database_url is None:
        database_url = get_database_url()
    
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True
    )
    
    logger.info(f"Created database engine with URL: {database_url}")
    return engine

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False)

def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    engine = get_engine()
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()