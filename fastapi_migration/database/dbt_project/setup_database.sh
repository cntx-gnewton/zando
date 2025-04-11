#!/bin/bash

# Setup script for initializing the Zando schema in an existing GCP Cloud SQL database

set -e

# Print section header
section() {
  echo ""
  echo "==============================================="
  echo "  $1"
  echo "==============================================="
  echo ""
}

# Check for .env file - required
if [ ! -f .env ]; then
  section "ERROR: Missing .env file"
  echo "The .env file is required for Cloud SQL connection details."
  echo "Please create a .env file with the following variables:"
  echo "  DB_USER=postgres"
  echo "  DB_PASS=your_password"
  echo "  DB_NAME=test"
  echo "  INSTANCE_CONNECTION_NAME=project-id:region:instance-name"
  exit 1
fi

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)
echo "Loaded environment variables from .env file"

# Validate required environment variables
if [ -z "$DB_USER" ] || [ -z "$DB_PASS" ] || [ -z "$DB_NAME" ] || [ -z "$INSTANCE_CONNECTION_NAME" ]; then
  section "ERROR: Missing required environment variables"
  echo "The following variables must be set in your .env file:"
  echo "  DB_USER: ${DB_USER:-MISSING}"
  echo "  DB_PASS: ${DB_PASS:+SET} ${DB_PASS:-MISSING}"
  echo "  DB_NAME: ${DB_NAME:-MISSING}"
  echo "  INSTANCE_CONNECTION_NAME: ${INSTANCE_CONNECTION_NAME:-MISSING}"
  exit 1
fi

section "Database Connection Details"
echo "DB_USER: $DB_USER"
echo "DB_NAME: $DB_NAME"
echo "INSTANCE_CONNECTION_NAME: $INSTANCE_CONNECTION_NAME"
echo "Using Google Cloud SQL connection"

# Check for Cloud SQL Auth Proxy
section "Checking Cloud SQL Auth Proxy"
if ! pgrep -f "cloud_sql_proxy.*$INSTANCE_CONNECTION_NAME" > /dev/null; then
  echo "WARNING: Cloud SQL Auth Proxy does not appear to be running for $INSTANCE_CONNECTION_NAME"
  echo "You may need to run the proxy in another terminal with:"
  echo "  cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:5432"
  
  # Ask if user wants to proceed anyway
  read -p "Do you want to continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting setup. Please start the Cloud SQL Auth Proxy and try again."
    exit 1
  fi
else
  echo "Cloud SQL Auth Proxy is running for $INSTANCE_CONNECTION_NAME"
fi

# Build connection parameters for local proxy
PSQL_ARGS="-h localhost -U $DB_USER -d $DB_NAME"

# Check database connection through proxy
section "Testing database connection"
if command -v psql &> /dev/null; then
  echo "Attempting to connect to Cloud SQL database via proxy..."
  
  # Test connection
  if PGPASSWORD=$DB_PASS psql $PSQL_ARGS -c "SELECT 1" > /dev/null 2>&1; then
    echo "Successfully connected to database."
  else
    echo "Error: Could not connect to database through Cloud SQL Auth Proxy."
    echo "Please check your credentials and proxy setup."
    exit 1
  fi
else
  echo "Error: psql command not found. Please install PostgreSQL client tools."
  exit 1
fi

# Run the schema creation script
section "Creating initial schema"
if [ -f schema.sql ]; then
  echo "Applying schema to Cloud SQL database..."
  if PGPASSWORD=$DB_PASS psql $PSQL_ARGS -f schema.sql; then
    echo "Schema applied successfully."
  else
    echo "Error: Failed to apply schema"
    exit 1
  fi
else
  echo "Error: schema.sql not found."
  exit 1
fi

section "Database setup complete!"
echo "You can now run setup.sh to initialize the dbt project."