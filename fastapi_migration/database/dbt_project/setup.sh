#!/bin/bash

# Setup script for Zando dbt project with Google Cloud SQL

set -e

# Check for .env file - required
if [ ! -f .env ]; then
  echo "ERROR: Missing .env file"
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
  echo "ERROR: Missing required environment variables in .env file."
  echo "Required variables: DB_USER, DB_PASS, DB_NAME, INSTANCE_CONNECTION_NAME"
  exit 1
fi

# Set target based on Cloud SQL Proxy status
if pgrep -f "cloud_sql_proxy.*$INSTANCE_CONNECTION_NAME" > /dev/null; then
  DBT_TARGET="gcp_proxy"
  echo "Detected Cloud SQL Auth Proxy running - using gcp_proxy target"
else
  echo "WARNING: Cloud SQL Auth Proxy not detected for $INSTANCE_CONNECTION_NAME"
  echo "If running locally, start the proxy in another terminal:"
  echo "  cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:5432"
  echo ""
  
  # Ask if this is running in a container/GCP environment
  read -p "Are you running in GCP environment? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    DBT_TARGET="gcp"
    echo "Using gcp target for direct socket connection"
  else
    DBT_TARGET="gcp_proxy"
    echo "Using gcp_proxy target, but proxy might not be running"
  fi
fi

# Print section header
section() {
  echo ""
  echo "==============================================="
  echo "  $1"
  echo "==============================================="
  echo ""
}

section "Database Connection Details"
echo "DB_USER: $DB_USER"
echo "DB_NAME: $DB_NAME"
echo "DBT_TARGET: $DBT_TARGET"

if [ -n "$INSTANCE_CONNECTION_NAME" ]; then
  echo "INSTANCE_CONNECTION_NAME: $INSTANCE_CONNECTION_NAME"
fi

# Check if dbt is installed
section "Checking dbt installation"
if ! command -v dbt &> /dev/null; then
  echo "dbt is not installed. Installing dbt-postgres..."
  pip install dbt-postgres
else
  echo "dbt is already installed: $(dbt --version | head -n 1)"
fi

# Create profiles directory if it doesn't exist
section "Setting up dbt profiles"
mkdir -p ~/.dbt

# Copy profiles if it doesn't exist
if [ ! -f ~/.dbt/profiles.yml ]; then
  echo "Creating profiles.yml in ~/.dbt..."
  cp profiles.yml.example ~/.dbt/profiles.yml
  echo "Created ~/.dbt/profiles.yml"
  echo "Please edit ~/.dbt/profiles.yml with your database credentials"
else
  echo "dbt profile already exists at ~/.dbt/profiles.yml"
  echo "If you need to update it, edit manually or replace with profiles.yml.example"
  
  # Offer to update the existing profile
  read -p "Do you want to update your existing profiles.yml with the new template? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp profiles.yml.example ~/.dbt/profiles.yml
    echo "Updated ~/.dbt/profiles.yml"
  fi
fi

# Test the connection
section "Testing dbt connection"
DBT_TARGET=$DBT_TARGET dbt debug

# Check if debug was successful before proceeding
if [ $? -ne 0 ]; then
  echo "dbt debug failed. Please check your database connection and profiles.yml."
  echo "You may need to run the Cloud SQL Auth Proxy if connecting to Google Cloud SQL."
  exit 1
fi

# Run setup
section "Building dbt project"
echo "Running dbt deps to install dependencies..."
DBT_TARGET=$DBT_TARGET dbt deps

echo "Loading seed data..."
DBT_TARGET=$DBT_TARGET dbt seed --full-refresh

echo "Building models..."
DBT_TARGET=$DBT_TARGET dbt run

section "Setup complete!"
echo "Your dbt project is ready to use."
echo ""
echo "Common commands (with current target: $DBT_TARGET):"
echo "  DBT_TARGET=$DBT_TARGET dbt seed          # Load seed data"
echo "  DBT_TARGET=$DBT_TARGET dbt run           # Run all models"
echo "  DBT_TARGET=$DBT_TARGET dbt test          # Run all tests"
echo "  DBT_TARGET=$DBT_TARGET dbt docs generate # Generate documentation"
echo "  DBT_TARGET=$DBT_TARGET dbt docs serve    # Serve documentation locally"
echo ""
echo "For Google Cloud SQL connections, you may need to run:"
echo "  cloud_sql_proxy -instances=$INSTANCE_CONNECTION_NAME=tcp:5432"
echo ""