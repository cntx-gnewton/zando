# SQL Migration Manager Plan

## Overview
This document outlines the plan to create a Python SQL migration tool for managing the genomic analysis database. The tool will provide a structured way to create, update, and delete database components (tables, functions, sequences, types, views) with version control capabilities.

## Current Architecture

The current codebase includes:
- Database connection management via Google Cloud SQL connector
- Connection pooling with both sync and async sessions
- Structured SQL files organized by component type
- Support for deployment in both local and cloud environments

## Migration Tool Requirements

1. **Version Management**
   - Track database schema versions
   - Support incremental migrations
   - Enable rollback to previous states

2. **Component Operations**
   - Create/delete tables
   - Create/delete functions
   - Create/delete sequences
   - Create/delete types
   - Create/delete views
   - Execute raw SQL scripts

3. **Environment Support**
   - Work with local PostgreSQL databases
   - Work with Google Cloud SQL instances
   - Handle authentication/connection differences

4. **Logging & Monitoring**
   - Track migration history
   - Log execution results
   - Support error handling and recovery

## Proposed Implementation

### 1. Migration Manager Core Class

The migration manager will execute raw SQL files rather than using Pydantic models or SQLAlchemy ORM. This approach provides several benefits:
- Full control over complex PostgreSQL features (custom types, stored procedures, complex constraints)
- Direct execution of existing SQL scripts without conversion
- Clearer separation between migration logic and application models

```python
class SqlMigrationManager:
    """
    Manages database migrations and schema changes for the genomic analysis database.
    
    This class provides methods to apply and roll back migrations for various
    database components (tables, functions, sequences, types, views) by executing
    SQL files directly.
    """
    
    def __init__(self, db_session=None, config_path=None):
        """Initialize the migration manager with a database session."""
        self.session = db_session or get_sync_db()
        self.config = self._load_config(config_path)
        self.migration_history = self._load_migration_history()
        
    def migrate_up(self, component_type=None, version=None):
        """Apply migrations to reach the specified version."""
        components = self._get_components_in_order(component_type)
        
        for component in components:
            sql_file = f"sql/{component}/up.sql"
            if os.path.exists(sql_file):
                self._execute_sql_file(sql_file)
                self._record_migration(component, version or "latest", "up")
        
    def migrate_down(self, component_type=None, version=None):
        """Roll back migrations to the specified version."""
        components = self._get_components_in_order(component_type, reverse=True)
        
        for component in components:
            sql_file = f"sql/{component}/down.sql"
            if os.path.exists(sql_file):
                self._execute_sql_file(sql_file)
                self._record_migration(component, version or "latest", "down")
        
    def get_current_version(self, component_type=None):
        """Get the current database schema version."""
        pass
        
    def _execute_sql_file(self, file_path):
        """Execute SQL from a file."""
        with open(file_path, 'r') as f:
            sql = f.read()
            
        with self.session() as session:
            # Execute SQL statements
            try:
                session.execute(sqlalchemy.text(sql))
                session.commit()
                logging.info(f"Successfully executed {file_path}")
                return True
            except Exception as e:
                session.rollback()
                logging.error(f"Error executing {file_path}: {str(e)}")
                raise
        
    def _get_components_in_order(self, component_type=None, reverse=False):
        """Get components in dependency order."""
        component_order = ["types", "sequences", "tables", "functions", "views", "config"]
        
        if component_type == "all" or component_type is None:
            components = component_order
        else:
            components = [component_type]
            
        if reverse:
            components = list(reversed(components))
            
        return components
        
    def _load_config(self, config_path):
        """Load migration configuration."""
        pass
        
    def _load_migration_history(self):
        """Load migration history from the database."""
        pass
        
    def _record_migration(self, component_type, version, direction):
        """Record a migration in the history table."""
        pass
```

### 2. Component Operations

Instead of component-specific classes, the migration manager will focus on executing the SQL files within each component directory:

```python
def apply_specific_migration(self, component_type, filename):
    """
    Apply a specific migration file for a component.
    
    Args:
        component_type: The type of component (tables, functions, etc.)
        filename: The SQL file to execute
    """
    file_path = f"sql/{component_type}/{filename}"
    if os.path.exists(file_path):
        return self._execute_sql_file(file_path)
    else:
        logging.warning(f"Migration file not found: {file_path}")
        return False
```

### 3. Migration Configuration Schema

Create a YAML configuration file for migration settings:

```yaml
# migrations.yaml
database:
  default_schema: public
  migration_table: schema_migrations
  
components:
  - name: types
    order: 1
    directory: sql/types
    
  - name: sequences
    order: 2
    directory: sql/sequences
    
  - name: tables
    order: 3
    directory: sql/tables
    
  - name: functions 
    order: 4
    directory: sql/functions
    
  - name: views
    order: 5
    directory: sql/views
    
  - name: config
    order: 6
    directory: sql/config
```

### 4. Migration History Table

Create a table to track migration history:

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    component_type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    direction VARCHAR(5) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details TEXT
);
```

### 5. Command-Line Interface

Create a CLI for running migrations:

```python
# migrate.py
import argparse
from migration_manager import SqlMigrationManager

def main():
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument('--direction', choices=['up', 'down'], default='up',
                       help='Migration direction (up or down)')
    parser.add_argument('--component', choices=['all', 'tables', 'functions', 'types', 'sequences', 'views', 'config'],
                       default='all', help='Component type to migrate')
    parser.add_argument('--version', help='Target version to migrate to')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--file', help='Execute a specific SQL file')
    
    args = parser.parse_args()
    
    manager = SqlMigrationManager(config_path=args.config)
    
    if args.file:
        manager.apply_specific_migration(args.component, args.file)
    elif args.direction == 'up':
        manager.migrate_up(args.component, args.version)
    else:
        manager.migrate_down(args.component, args.version)

if __name__ == '__main__':
    main()
```

### 6. Execution Order Management

To handle the dependencies between components, the tool will enforce a specific order of execution:

1. **Creating the database:**
   - First: Types
   - Second: Sequences
   - Third: Tables
   - Fourth: Functions
   - Fifth: Views
   - Sixth: Configuration

2. **Dropping the database (reverse order):**
   - First: Configuration
   - Second: Views
   - Third: Functions
   - Fourth: Tables
   - Fifth: Sequences
   - Sixth: Types

## Implementation Timeline

1. Create migration configuration schema and loading logic
2. Implement core SqlMigrationManager class with file execution capabilities 
3. Create migration history table and tracking functionality
4. Build CLI interface
5. Add testing and validation capabilities
6. Document usage and examples

## Conclusion

This migration manager will provide a structured approach to database schema management using raw SQL files. This approach gives you full control over the database schema while providing the convenience of version management and automated deployment. The tool will work with both local development environments and Google Cloud SQL production deployments.