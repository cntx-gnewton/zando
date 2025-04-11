#!/bin/bash

# Setup script for Zando database management environment

# Detect the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="${SCRIPT_DIR}/venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"

# Print section header
section() {
  echo ""
  echo "==============================================="
  echo "  $1"
  echo "==============================================="
  echo ""
}

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
  section "Creating virtual environment"
  python3 -m venv "$VENV_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
  fi
fi

# Activate virtual environment
section "Activating virtual environment"
source "${VENV_DIR}/bin/activate"
if [ $? -ne 0 ]; then
  echo "Error: Failed to activate virtual environment"
  exit 1
fi

# Install dependencies
section "Installing dependencies"
if [ -f "$REQUIREMENTS_FILE" ]; then
  pip install -r "$REQUIREMENTS_FILE"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
  fi
else
  echo "Warning: Requirements file not found at $REQUIREMENTS_FILE"
fi

# Check if PostgreSQL is running
section "Checking PostgreSQL connection"
if ! command -v pg_isready &> /dev/null; then
  echo "Warning: pg_isready command not found. Skipping PostgreSQL check."
else
  if ! pg_isready > /dev/null; then
    echo "ERROR: PostgreSQL is not running. Please start PostgreSQL and try again."
    exit 1
  else
    echo "PostgreSQL is running."
  fi
fi

# Create the database if it doesn't exist
if command -v psql &> /dev/null; then
  if ! psql -lqt | cut -d \| -f 1 | grep -qw zando; then
    section "Creating database 'zando'"
    createdb zando
    if [ $? -ne 0 ]; then
      echo "Error: Failed to create database 'zando'"
      exit 1
    fi
  else
    echo "Database 'zando' already exists."
  fi
else
  echo "Warning: psql command not found. Skipping database creation."
fi

# Initialize Alembic if needed
if [ ! -d "${SCRIPT_DIR}/migrations/versions" ]; then
  section "Initializing Alembic"
  echo "Creating initial migration..."
  python "${SCRIPT_DIR}/init_alembic.py"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to initialize Alembic"
    exit 1
  fi
fi

# Print usage information
section "Setup complete!"
echo "Your database management environment is ready."
echo ""
echo "To use the database management tools, run:"
echo "  source ${SCRIPT_DIR}/venv/bin/activate"
echo "  cd ${SCRIPT_DIR}"
echo ""
echo "Available commands:"
echo "  cd migrations && alembic upgrade head    # Apply all migrations"
echo "  cd migrations && alembic revision --autogenerate -m 'description'   # Create a new migration"
echo "  python init_alembic.py                   # Create initial migration"
echo ""
echo "You can also run these commands directly if the virtual environment is active."