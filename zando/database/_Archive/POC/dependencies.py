from typing import Generator, AsyncGenerator
from fastapi import Depends
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from google_session import SessionLocal

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting a database session.
    
    Yields an AsyncSession using our SimpleAsyncSession implementation,
    which provides an async interface over the synchronous Google Cloud SQL connector.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        # Explicitly close the session to clean up resources
        try:
            await session.close()
        except Exception as e:
            logger.warning(f"Error closing database session: {e}")

# For compatibility with code that requires a synchronous db session
def get_sync_db():
    """
    Dependency for getting a synchronous database session.
    This is useful for background tasks or code that doesn't need async.
    """
    from google_session import SyncSessionLocal
    
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        try:
            session.close()
        except Exception as e:
            logger.warning(f"Error closing sync database session: {e}")