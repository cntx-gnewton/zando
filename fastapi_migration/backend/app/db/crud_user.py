from typing import Optional, Union, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.db.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get a user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_email = await get_user_by_email(db, user_in.email)
    if existing_email:
        raise ValueError("Email already registered")
    
    existing_username = await get_user_by_username(db, user_in.username)
    if existing_username:
        raise ValueError("Username already taken")
    
    # Create new user
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_superuser=False,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(
    db: AsyncSession, db_user: User, user_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """Update a user."""
    user_data = user_in if isinstance(user_in, dict) else user_in.model_dump(exclude_unset=True)
    
    # If password is being updated, hash it
    if "password" in user_data and user_data["password"]:
        password = user_data.pop("password")
        user_data["hashed_password"] = get_password_hash(password)
    
    # Update user in database
    stmt = (
        update(User)
        .where(User.id == db_user.id)
        .values(**user_data)
    )
    await db.execute(stmt)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[User]:
    """Get a list of users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def activate_user(db: AsyncSession, db_user: User) -> User:
    """Activate a user."""
    db_user.is_active = True
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def deactivate_user(db: AsyncSession, db_user: User) -> User:
    """Deactivate a user."""
    db_user.is_active = False
    await db.commit()
    await db.refresh(db_user)
    return db_user