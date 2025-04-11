# Zando DBT Project

This dbt (data build tool) project manages the database schema and transformations for the Zando genomic analysis platform.

## Overview

The database system has been refactored from monolithic SQL scripts to a maintainable and version-controlled approach using dbt.

Key features:
- Structured table definitions using SQL models
- Version-controlled schema changes
- CSV-based seed data for reference tables
- Mart models for complex queries and aggregations
- Compatible with both local development and Google Cloud SQL

## Directory Structure

```
/dbt_project
  /models              # dbt model definitions (SQL files)
    /core              # Base tables mapped from source data
    /marts             # Transformed data for analysis
  /seeds               # CSV files for reference data
  /macros              # Reusable SQL snippets
  /snapshots           # Point-in-time snapshots
  /tests               # Data validation tests
  /analysis            # Ad-hoc analysis queries
  dbt_project.yml      # Project configuration
  profiles.yml.example # Database connection profiles
  schema.sql           # Initial schema creation script
  setup.sh             # Setup script for dbt project
  setup_database.sh    # Database initialization script
```

## Quick Setup

### 1. Configure the Database Connection

Create a `.env` file with your Google Cloud SQL connection details:

```bash
DB_USER="postgres"
DB_PASS="postgres" 
DB_NAME="test"
INSTANCE_CONNECTION_NAME="zerosandones-369:us-central1:zando-dev"
```

### 2. Run the Cloud SQL Auth Proxy

For local development, you need to run the Cloud SQL Auth Proxy:

```bash
# Install the proxy if needed
# https://cloud.google.com/sql/docs/postgres/connect-admin-proxy

# Run the proxy in a separate terminal
cloud_sql_proxy -instances=zerosandones-369:us-central1:zando-dev=tcp:5432
```

### 3. Initialize the Database Schema

Apply the initial schema to your Google Cloud SQL database:

```bash
./setup_database.sh
```

This script will:
- Check that your `.env` file contains the required variables
- Verify that the Cloud SQL Auth Proxy is running
- Test the connection to your database
- Apply the initial schema (tables and types) to your database

### 4. Set Up DBT Project

Next, initialize the dbt project:

```bash
./setup.sh
```

This script will:
- Install dbt-postgres if not already installed
- Set up the profiles configuration
- Test the database connection
- Load seed data and build initial models

## Using DBT

Once set up, you can use standard dbt commands:

### Load Seed Data

```bash
dbt seed
```

This loads reference data from CSV files into the database.

### Run Models

```bash
# Run all models
dbt run

# Run specific models
dbt run --select core
dbt run --select marts.genetic_findings
```

### Testing

```bash
# Run all tests
dbt test

# Test specific models
dbt test --select core.snp
```

### Documentation

```bash
# Generate docs
dbt docs generate

# Serve docs website
dbt docs serve
```

## Model Descriptions

### Core Models

- `snp` - Genetic variants with their effects
- `skin_characteristic` - Skin traits affected by genetic variations
- `skin_condition` - Specific skin conditions
- `ingredient` - Beneficial ingredients
- `ingredient_caution` - Ingredients to avoid

### Relationship Models

- `snp_characteristic_link` - Links SNPs to skin characteristics
- `characteristic_condition_link` - Links characteristics to conditions
- `condition_ingredient_link` - Links conditions to ingredients
- `snp_ingredient_link` - Links SNPs to beneficial ingredients
- `snp_ingredient_caution_link` - Links SNPs to ingredients to avoid

### Mart Models

- `genetic_findings` - Consolidated view of genetic findings with related characteristics and ingredients

## Environment Configuration

The setup script will create a `.dbt/profiles.yml` file based on your `.env` variables. The default configuration includes:

```yaml
zando:
  outputs:
    # For local testing (not used in this project)
    dev:
      type: postgres
      host: localhost
      user: postgres
      password: postgres
      port: 5432
      dbname: test
      schema: public
      threads: 4
    
    # For Google Cloud SQL with proxy running locally
    gcp_proxy:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      password: postgres
      dbname: test
      schema: public
      threads: 4
    
    # For Google Cloud SQL in Cloud Run environment
    gcp:
      type: postgres
      host: /cloudsql/zerosandones-369:us-central1:zando-dev
      user: postgres
      password: postgres
      port: 5432
      dbname: test
      schema: public
      threads: 4

  target: gcp_proxy  # Default target for local development with proxy
```

You can use environment variables to configure your database connection:

```bash
# These are automatically read from your .env file
export DB_USER=postgres
export DB_PASS=postgres
export DB_NAME=test
export INSTANCE_CONNECTION_NAME=zerosandones-369:us-central1:zando-dev

# You can also set this explicitly if needed
export DBT_TARGET=gcp_proxy  # Options: gcp_proxy for local development, gcp for Cloud Run environment
```

## Integration with FastAPI

This dbt project can be integrated with the FastAPI backend by:
1. Directly querying the tables/views created by dbt
2. Using dbt's RPC server for real-time model execution
3. Scheduling dbt runs for periodic data refreshes

API integration code will be implemented in the next phase.