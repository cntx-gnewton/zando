# Zando Database Management

This directory contains the database schema, migrations, data files, and management scripts for the Zando genomic analysis platform. The database has been refactored to use SQLAlchemy ORM models and Alembic for migrations, providing better maintainability and developer experience.

## Directory Structure

```
/db
  /migrations           # Alembic migration configuration and version files
    /versions           # Auto-generated migration script files
    alembic.ini         # Alembic configuration
    env.py              # Alembic environment configuration
    script.py.mako      # Template for migration files
  /models               # SQLAlchemy ORM models
    __init__.py         # Base model and imports
    snp.py              # SNP and relationship models
    characteristic.py   # Skin characteristic models
    condition.py        # Skin condition models
    ingredient.py       # Ingredient models
  /data                 # CSV files for all reference data
    snps.csv
    characteristics.csv
    ingredients.csv
    ingredient_cautions.csv
    relationships/      # CSV files for relationship tables
      snp_characteristic.csv
      characteristic_condition.csv
      snp_ingredient.csv
  /scripts              # Database management scripts
    db_connection.py    # Database connection utilities
    init_alembic.py     # Alembic initialization script
  config.yaml           # Configuration for different environments
  requirements.txt      # Python package dependencies
  setup.sh              # Setup script for development environment
```

## Setup Instructions

### Quick Setup

For a complete setup, simply run:

```bash
./setup.sh
```

This will:
1. Create a Python virtual environment
2. Install dependencies
3. Create the database if needed
4. Initialize Alembic and create initial migration if needed

### Manual Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the PostgreSQL database:
   ```bash
   createdb zando
   ```

4. Create initial migration:
   ```bash
   python init_alembic.py
   ```

5. Apply migrations:
   ```bash
   cd migrations
   alembic upgrade head
   ```

## Development Guidelines

### Working with Models

The database schema is defined using SQLAlchemy ORM models in the `models` directory. Key models include:

- `SNP`: Genetic variants with their effects
- `SkinCharacteristic`: Skin traits affected by genetic variants
- `SkinCondition`: Specific skin conditions
- `Ingredient/IngredientCaution`: Beneficial and cautionary ingredients
- Association tables: Linking entities together

### Creating New Migrations

Whenever you make changes to the models, create a new migration:

```bash
cd migrations
alembic revision --autogenerate -m "Description of changes"
```

Review the generated migration script in `migrations/versions/` before applying it.

### Applying Migrations

To apply all pending migrations:

```bash
cd migrations
alembic upgrade head
```

To roll back to a specific migration:

```bash
alembic downgrade <revision>
```

## CSV Format Requirements

All CSV files must:
- Have headers matching their corresponding table column names
- Use double quotes for fields containing commas, quotes, or special characters
- Use UTF-8 encoding

## Data Seeding

CSV files in the `data` directory are used to populate the database. The seeding process:

1. Loads CSV files into Python data structures
2. Resolves references between entities
3. Creates database records with proper relationships

To update reference data, edit the CSV files and rerun the seeding process.
