# Zando Database Management

This directory contains the SQLAlchemy ORM-based database system for the Zando genomic analysis platform, refactored from monolithic SQL scripts to a maintainable and version-controlled approach.

## Overview

The database system includes:

- **SQLAlchemy ORM Models** - Define the database schema using Python classes
- **Alembic Migration System** - Track and apply database schema changes
- **CSV-based Data Management** - Store reference data in easily editable CSV files
- **Google Cloud SQL Integration** - Support for both local and GCP database deployments
- **Seeding Framework** - Populate the database from CSV files

## Directory Structure

- `models/` - SQLAlchemy ORM model definitions
- `migrations/` - Alembic migration configuration and scripts
- `seed_data/` 
  - `csv/` - CSV files containing reference data
  - `seed_utils.py` - Utilities for loading from CSV files
- `db.py` - Database connection and session management
- `seed.py` - Database seeding orchestration
- `create_migration.py` - Utility to create initial migration

## Setup

### Prerequisites

- Python 3.7+
- PostgreSQL database or Google Cloud SQL access
- Python packages: SQLAlchemy, Alembic, python-dotenv, psycopg2-binary, etc.

### Environment Configuration

Create a `.env` file in the database directory with:

```
# For Google Cloud SQL
DB_USER="postgres"
DB_PASS="your_password"
DB_NAME="zando"
INSTANCE_CONNECTION_NAME="project-id:region:instance-name"

# For local development (optional)
DATABASE_URL="postgresql://localhost/zando"
```

### Quick Setup

1. **Create a virtual environment:**

   ```bash
   cd fastapi_migration/database
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create the initial migration:**

   ```bash
   python create_migration.py
   ```

4. **Apply the migration:**

   ```bash
   cd migrations
   alembic upgrade head
   ```

5. **Seed the database:**

   ```bash
   python seed.py
   ```

### Managing Migrations

#### Creating a New Migration

When changing database schema:

```
alembic revision --autogenerate -m "Description of changes"
```

#### Applying Migrations

To upgrade the database to the latest version:

```
alembic upgrade head
```

To upgrade to a specific version:

```
alembic upgrade <revision>
```

#### Rolling Back Migrations

To downgrade to a previous version:

```
alembic downgrade <revision>
```

### Managing Seed Data with CSV Files

All reference data is stored in CSV files for easy maintenance:

- `snps.csv` - Genetic variants
- `skin_characteristics.csv` - Skin characteristics
- `skin_conditions.csv` - Skin conditions  
- `ingredients.csv` - Beneficial ingredients
- `ingredient_cautions.csv` - Ingredients to avoid or use with caution

To modify the seed data:

1. Edit the appropriate CSV file
2. Run the seeding script to update the database:
   ```
   python seed.py --truncate
   ```

To add a new type of seed data:

1. Create a new CSV file in `seed_data/csv/`
2. Add a corresponding seed function in `seed.py`
3. Update the `seed_all()` function to call your new seed function

## Integration with FastAPI Backend

This database management system is designed to be integrated with the existing FastAPI backend. The integration involves:

1. Updating import paths in models to use `app.db.session.Base`
2. Using `app.db.session.get_db_engine()` in migrations
3. Integrating the seed script with the application startup

This process will be documented in more detail as the integration progresses.

## Adding New Models

1. Create a new model file in `models/`
2. Define your SQLAlchemy model class
3. Import the model in `models/__init__.py`
4. Generate a new migration with Alembic