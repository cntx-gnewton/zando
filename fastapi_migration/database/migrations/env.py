import logging
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is the Alembic Config object, which provides access to the values within the .ini file
config = context.config

# Set up logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Import all models for auto-generation of migrations
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to make imports work
sys.path.append(str(Path(__file__).parent.parent.parent))
the from fastapi_migration.database.models import Base
from fastapi_migration.database.db import get_db_engine

# Get target database URL from environment or config
def get_url():
    # Check for GCP database connection
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    instance_connection = os.getenv("INSTANCE_CONNECTION_NAME")
    
    if all([db_user, db_pass, db_name, instance_connection]):
        # Google Cloud SQL connection
        logger.info(f"Connecting to Google Cloud SQL instance: {instance_connection}")
        return f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock=/cloudsql/{instance_connection}/.s.PGSQL.5432"
    else:
        # For development, use a local database URL
        return os.getenv("DATABASE_URL", "postgresql://localhost/zando")

# This will be the base metadata that will be used for migration generation
target_metadata = Base.metadata

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Run migrations in 'online' mode.
    """
    # Use the existing engine when integrated with the app
    connectable = get_db_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()