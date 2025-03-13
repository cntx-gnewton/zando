from typing import Generator, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.db.session import SessionLocal
from app.core.security import oauth2_scheme
from app.core.config import settings
from app.db import crud_user
from app.db.models.user import User

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
    from app.db.session import SyncSessionLocal
    
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        try:
            session.close()
        except Exception as e:
            logger.warning(f"Error closing sync database session: {e}")

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Verifies the JWT token and returns the current user.
    
    Args:
        db: Database session
        token: JWT token from Authorization header
    
    Returns:
        User: The current authenticated user
    
    Raises:
        HTTPException: When the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get the user from the database
    user = await crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    # Check if the user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user. This is a simple wrapper around get_current_user
    that ensures the user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser. This is a dependency that ensures the user is a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user