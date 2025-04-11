# Zando Database Migration Tool

A SQL migration tool for managing the Zando genomic analysis database schema. This tool provides a structured way to create, update, and delete database components with version control capabilities.

## Features

- Manage database schema components (tables, functions, types, sequences, views)
- Apply and roll back migrations with defined execution order
- Execute SQL files directly with error handling
- Support for both local PostgreSQL and Google Cloud SQL
- Docker-ready for CI/CD pipelines

## Installation

### Local Development

```bash
# Using Poetry (recommended)
poetry install

# Using pip
pip install -e .
```

### Docker

```bash
# Build the Docker image
docker build -t zando-db-migrations .

# Run migrations using Docker
docker run --rm -v $(pwd)/sql:/app/sql zando-db-migrations --direction up
```

## Configuration

### Database Configuration

Create a `db_config.yaml` file with your database connection details:

```yaml
# Local development configuration
development:
  user: "postgres"
  password: "postgres"
  host: "localhost"
  port: 5432
  database: "postgres"
  use_gcp: false

# Production configuration for Google Cloud SQL
production:
  use_gcp: true
  instance_connection_name: "your-project:region:instance"
  user: "postgres"
  password: "your-password"
  database: "postgres"
  use_private_ip: false

# Default profile to use
active_profile: development
```

Alternatively, you can use environment variables:

```bash
export DB_USER=postgres
export DB_PASS=postgres
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export USE_GCP=false
export INSTANCE_CONNECTION_NAME=your-project:region:instance
```

## Usage

### Basic Commands

Apply all migrations:

```bash
# Using Poetry
poetry run migrate --direction up

# Using installed CLI
migrate --direction up
```

Roll back all migrations:

```bash
migrate --direction down
```

Apply migrations for a specific component:

```bash
migrate --direction up --component tables
```

Populate database tables with CSV data:

```bash
# Populate all tables
migrate --direction populate

# Populate a specific table
migrate --direction populate --table snp
```

### Advanced Options

Execute a specific SQL file:

```bash
migrate --file custom_migration.sql --component views
```

Execute all SQL files in a directory:

```bash
migrate --dir views/custom
```

Specify paths to configuration files and data directories:

```bash
migrate --config /path/to/migrations.yaml --db-config /path/to/db_config.yaml --data-dir /path/to/csv/files
```

## Database Component Order

The tool maintains the correct dependency order between components:

1. **Config** - Database configuration settings
2. **Types** - Custom PostgreSQL data types
3. **Tables** - Database tables and constraints
4. **Sequences** - Auto-increment sequences
5. **Functions** - Stored procedures and functions
6. **Views** - Database views

When rolling back, the order is reversed to respect dependencies.

## Directory Structure

The migration tool is designed to work with the following directory structure:

```
/
├── db_migrations/        # Python package for migration tool
├── db_config.yaml        # Database connection configuration
├── migrations.yaml       # Migration configuration
└── sql/                  # SQL files organized by component
    ├── config/
    │   ├── up.sql       # Script to apply configuration
    │   └── down.sql     # Script to remove configuration
    ├── types/
    │   ├── up.sql       # Script to create types
    │   └── down.sql     # Script to drop types
    ├── tables/
    │   ├── up.sql       # Script to create tables
    │   ├── down.sql     # Script to drop tables
    │   └── alter.sql    # Script for table alterations
    ├── sequences/
    │   ├── up.sql       # Script to create sequences
    │   └── down.sql     # Script to drop sequences
    ├── functions/
    │   ├── up.sql       # Script to create functions
    │   └── down.sql     # Script to drop functions
    └── views/
        ├── up.sql       # Script to create views
        └── down.sql     # Script to drop views
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Database Migration

on:
  push:
    branches: [ main ]
    paths:
      - 'sql/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: pip install -e .
        
      - name: Run migrations
        run: migrate --direction up
        env:
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASS: ${{ secrets.DB_PASS }}
          DB_NAME: ${{ secrets.DB_NAME }}
          INSTANCE_CONNECTION_NAME: ${{ secrets.INSTANCE_CONNECTION_NAME }}
          USE_GCP: "true"
```

## Troubleshooting

- **Connection Issues**: Verify credentials in `db_config.yaml` or environment variables
- **Permission Errors**: Ensure the database user has sufficient privileges
- **Order Problems**: Check if your migrations have interdependencies that require a specific order
- **GCP Connectivity**: Make sure the GCP connector is properly installed and configured

## License

This project is licensed under the MIT License - see the LICENSE file for details.