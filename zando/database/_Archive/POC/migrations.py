import os
import logging
import yaml
import sqlalchemy
from typing import List, Dict, Optional, Union, Any
from datetime import datetime

from dependencies import get_sync_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migration_manager")

class SqlMigrationManager:
    """
    Manages database migrations and schema changes for the genomic analysis database.
    
    This class provides methods to apply and roll back migrations for various
    database components (tables, functions, sequences, types, views) by executing
    SQL files directly.
    """
    
    def __init__(self, db_session=None, config_path: str = None):
        """Initialize the migration manager with a database session."""
        # For sync_db, we need to use the factory function, not the generator itself
        from google_session import SyncSessionLocal
        self.session = db_session or SyncSessionLocal
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'migrations.yaml')
        self.config = self._load_config(self.config_path)
        
    def migrate_up(self, component_type: str = None, version: str = None) -> bool:
        """
        Apply migrations to reach the specified version.
        
        Args:
            component_type: The type of component to migrate (tables, functions, etc.)
                            or 'all' for all components
            version: The target version to migrate to (defaults to 'latest')
            
        Returns:
            True if successful, False otherwise
        """
        components = self._get_components_in_order(component_type)
        
        logger.info(f"Running migrations UP for components: {components}")
        success = True
        
        for component in components:
            sql_file = os.path.join(os.path.dirname(__file__), f"sql/{component}/up.sql")
            if os.path.exists(sql_file):
                logger.info(f"Applying {component} migration from {sql_file}")
                try:
                    self._execute_sql_file(sql_file)
                    logger.info(f"Successfully applied {component} migration")
                except Exception as e:
                    logger.error(f"Error applying {component} migration: {str(e)}")
                    success = False
                    break
            else:
                logger.warning(f"Migration file not found: {sql_file}")
                
        return success
        
    def migrate_down(self, component_type: str = None, version: str = None) -> bool:
        """
        Roll back migrations to the specified version.
        
        Args:
            component_type: The type of component to roll back (tables, functions, etc.)
                           or 'all' for all components
            version: The target version to roll back to (defaults to removing everything)
            
        Returns:
            True if successful, False otherwise
        """
        components = self._get_components_in_order(component_type, reverse=True)
        
        logger.info(f"Running migrations DOWN for components: {components}")
        success = True
        
        for component in components:
            sql_file = os.path.join(os.path.dirname(__file__), f"sql/{component}/down.sql")
            if os.path.exists(sql_file):
                logger.info(f"Rolling back {component} migration from {sql_file}")
                try:
                    self._execute_sql_file(sql_file)
                    logger.info(f"Successfully rolled back {component} migration")
                except Exception as e:
                    logger.error(f"Error rolling back {component} migration: {str(e)}")
                    success = False
                    break
            else:
                logger.warning(f"Migration file not found: {sql_file}")
                
        return success
    
    def apply_specific_migration(self, component_type: str, filename: str) -> bool:
        """
        Apply a specific migration file for a component.
        
        Args:
            component_type: The type of component (tables, functions, etc.)
            filename: The SQL file to execute
            
        Returns:
            True if successful, False otherwise
        """
        file_path = os.path.join(os.path.dirname(__file__), f"sql/{component_type}/{filename}")
        if os.path.exists(file_path):
            logger.info(f"Applying specific migration: {file_path}")
            try:
                self._execute_sql_file(file_path)
                logger.info(f"Successfully applied specific migration: {filename}")
                return True
            except Exception as e:
                logger.error(f"Error applying specific migration: {str(e)}")
                return False
        else:
            logger.warning(f"Migration file not found: {file_path}")
            return False
            
    def apply_directory_migrations(self, directory: str) -> bool:
        """
        Apply all SQL files in a directory.
        
        Args:
            directory: Path to directory containing SQL files
            
        Returns:
            True if successful, False otherwise
        """
        dir_path = os.path.join(os.path.dirname(__file__), directory)
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            logger.warning(f"Directory not found: {dir_path}")
            return False
            
        logger.info(f"Applying all migrations in directory: {dir_path}")
        success = True
        
        # Get all SQL files in directory
        sql_files = [f for f in os.listdir(dir_path) if f.endswith('.sql')]
        
        for sql_file in sorted(sql_files):
            file_path = os.path.join(dir_path, sql_file)
            logger.info(f"Applying migration: {file_path}")
            try:
                self._execute_sql_file(file_path)
                logger.info(f"Successfully applied migration: {sql_file}")
            except Exception as e:
                logger.error(f"Error applying migration {sql_file}: {str(e)}")
                success = False
                break
                
        return success
           
    def _execute_sql_file(self, file_path: str) -> bool:
        """
        Execute SQL from a file.
        
        Args:
            file_path: Path to the SQL file
            
        Returns:
            True if successful
            
        Raises:
            Exception if SQL execution fails
        """
        with open(file_path, 'r') as f:
            sql = f.read()
            
        with self.session() as session:
            # Execute SQL statements
            try:
                session.execute(sqlalchemy.text(sql))
                session.commit()
                logger.info(f"Successfully executed {file_path}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error executing {file_path}: {str(e)}")
                raise
    
    def _get_components_in_order(self, component_type: str = None, reverse: bool = False) -> List[str]:
        """
        Get components in dependency order.
        
        Args:
            component_type: Optional specific component type
            reverse: Whether to reverse the order (for down migrations)
            
        Returns:
            List of component names in the correct order
        """
        component_order = ["config", "types", "tables", "sequences", "functions", "views"]
        
        if component_type == "all" or component_type is None:
            components = component_order
        elif component_type in component_order:
            components = [component_type]
        else:
            raise ValueError(f"Unknown component type: {component_type}")
            
        if reverse:
            components = list(reversed(components))
            
        return components
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load migration configuration.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
        """
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        else:
            logger.warning(f"Configuration file not found: {config_path}, using defaults")
            # Default configuration
            return {
                "database": {
                    "default_schema": "public"
                },
                "components": [
                    {"name": "config", "order": 1, "directory": "sql/config"},
                    {"name": "types", "order": 2, "directory": "sql/types"},
                    {"name": "tables", "order": 3, "directory": "sql/tables"},
                    {"name": "sequences", "order": 4, "directory": "sql/sequences"},
                    {"name": "functions", "order": 5, "directory": "sql/functions"},
                    {"name": "views", "order": 6, "directory": "sql/views"}
                ]
            }