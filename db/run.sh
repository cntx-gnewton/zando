#!/bin/bash

# Run script for Zando database management tools

# Detect the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="${SCRIPT_DIR}/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Please run setup.sh first."
  exit 1
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Process arguments
if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [options]"
  echo "Available commands: init, migrate, check, reset"
  exit 1
fi

COMMAND=$1
shift 1

# Parse --env argument if present
ENV="development"
for (( i=1; i<=$#; i++ )); do
  if [[ "${!i}" == "--env" ]]; then
    j=$((i+1))
    if [ $j -le $# ]; then
      ENV="${!j}"
    fi
    break
  fi
done

# Run with proper arguments
python "${SCRIPT_DIR}/scripts/manage.py" "--env" "$ENV" "$COMMAND" "$@"

# Deactivate virtual environment
deactivate