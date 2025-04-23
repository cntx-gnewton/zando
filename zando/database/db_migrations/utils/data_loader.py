import os
import csv
import logging
import sqlalchemy
from sqlalchemy.dialects.postgresql import insert

from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Utility class for loading CSV data into database tables.
    
    This class provides methods to read CSV files and insert
    the data into corresponding database tables.
    """
    
    def __init__(self, session_factory, data_dir: str = None):
        """
        Initialize the data loader.
        
        Args:
            session_factory: SQLAlchemy session factory
            data_dir: Directory containing CSV data files
        """
        self.session = session_factory
        
        # Set data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # Default to data directory relative to package
            self.data_dir = Path(os.getcwd()) / "data"
    
    def load_all_data(self) -> bool:
        """
        Load data from all CSV files in the data directory.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Loading data from {self.data_dir}")
        
        # Define the order of tables to load data into for proper referential integrity
        table_order = [
            "snp.csv:snp",
            "skincharacteristic.csv:skincharacteristic",
            "snp_characteristic_link.csv:snp_characteristic_link",
            "skincondition.csv:skincondition",
            "characteristic_condition_link.csv:characteristic_condition_link",
            "ingredient.csv:ingredient",
            "ingredientcaution.csv:ingredientcaution",
            "snp_ingredient_link.csv:snp_ingredient_link",
            "snp_ingredientcaution_link.csv:snp_ingredientcaution_link",
            "condition_ingredient_link.csv:condition_ingredient_link",
        ]
        
        success = True
        
        for file_table_pair in table_order:
            parts = file_table_pair.split(':')
            if len(parts) != 2:
                logger.warning(f"Invalid file-table pair format: {file_table_pair}")
                continue
                
            file_path, table_name = parts
            file_path = self.data_dir / file_path
            
            if not file_path.exists():
                logger.warning(f"CSV file not found: {file_path}")
                continue
                
            logger.info(f"Loading data from {file_path} into table {table_name}")
            
            try:
                records = self._read_csv(file_path)
                if records:
                    success = success and self._insert_data(table_name, records)
            except Exception as e:
                logger.error(f"Error loading data from {file_path}: {str(e)}")
                success = False
                
        return success
    
    def load_table_data(self, table_name: str, file_path: Optional[str] = None) -> bool:
        """
        Load data into a specific table from a CSV file.
        
        Args:
            table_name: Name of the database table
            file_path: Path to the CSV file (if not specified, will look for a file with the same name as the table)
            
        Returns:
            True if successful, False otherwise
        """
        if not file_path:
            # Try to guess the file path based on table name
            mapping = {
                "snp": "snps.csv",
                "skincharacteristic": "characteristics.csv",
                "skincondition": "skin_conditions.csv",
                "ingredient": "ingredients.csv",
                "ingredientcaution": "ingredient_cautions.csv",
                "snp_characteristic_link": "relationships/snp_characteristic.csv",
                "characteristic_condition_link": "relationships/characteristic_condition.csv",
                "snp_ingredient_link": "relationships/snp_ingredient.csv",
                "snp_ingredientcaution_link": "relationships/snp_ingredientcaution.csv",
                "condition_ingredient_link": "relationships/condition_ingredient.csv"
            }
            
            if table_name in mapping:
                file_path = self.data_dir / mapping[table_name]
            else:
                file_path = self.data_dir / f"{table_name}.csv"
        else:
            file_path = Path(file_path)
            
        if not file_path.exists():
            logger.warning(f"CSV file not found: {file_path}")
            return False
            
        logger.info(f"Loading data from {file_path} into table {table_name}")
        
        try:
            records = self._read_csv(file_path)
            if records:
                return self._insert_data(table_name, records)
            return False
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return False
    
    def _read_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Read data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of dictionaries representing the CSV records
        """
        records = []
        
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Clean up the row data
                clean_row = {}
                for key, value in row.items():
                    if key:  # Skip empty column names
                        # Convert empty strings to None for database compatibility
                        clean_row[key.strip()] = None if value == '' else value
                records.append(clean_row)
                
        logger.info(f"Read {len(records)} records from {file_path}")
        return records
    
    def _insert_data(self, table_name: str, records: List[Dict[str, Any]]) -> bool:
        """
        Insert data into a database table.
        
        Args:
            table_name: Name of the database table
            records: List of dictionaries containing the data to insert
            
        Returns:
            True if successful, False otherwise
        """
        if not records:
            logger.warning(f"No records to insert into {table_name}")
            return True
            
        with self.session() as session:
            try:
                # Use bulk insert
                metadata = sqlalchemy.MetaData()
                table = sqlalchemy.Table(table_name, metadata, autoload_with=session.bind)
                
                # Create insert statement
                stmt = insert(table).values(records)
                
                # Use on conflict do nothing to handle duplicates gracefully
                stmt = stmt.on_conflict_do_nothing()
                
                session.execute(stmt)
                session.commit()
                
                logger.info(f"Successfully inserted {len(records)} records into {table_name}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error inserting data into {table_name}: {e}")
                raise