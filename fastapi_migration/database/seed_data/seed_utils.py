"""
Utility functions for seeding the database from CSV files.

This module provides helper functions for loading data from CSV files
and transforming it into the format needed for database seeding.
"""

import os
import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_csv_path(file_name):
    """
    Get the full path to a CSV file in the seed_data/csv directory.
    
    Args:
        file_name: Name of the CSV file (with or without .csv extension)
        
    Returns:
        Path to the CSV file
    """
    # Ensure file_name has .csv extension
    if not file_name.endswith('.csv'):
        file_name = f"{file_name}.csv"
        
    # Get the directory of this script
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Construct path to CSV file
    csv_path = current_dir / 'csv' / file_name
    
    return csv_path

def load_csv_data(file_name):
    """
    Load data from a CSV file into a list of dictionaries.
    
    Args:
        file_name: Name of the CSV file (with or without .csv extension)
        
    Returns:
        List of dictionaries with column names as keys
    """
    csv_path = get_csv_path(file_name)
    
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return []
    
    data = []
    
    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        # Use DictReader to automatically use first row as column names
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Create a dictionary with column keys mapping to row values
            # Strip whitespace from string values
            clean_row = {key: value.strip() if isinstance(value, str) else value 
                         for key, value in row.items()}
            data.append(clean_row)
    
    logger.info(f"Loaded {len(data)} rows from {file_name}")
    return data