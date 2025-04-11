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

```python
class SqlMigrationManager:
    """
    Manages database migrations and schema changes for the genomic analysis database.
    
    This class provides methods to apply and roll back migrations for various
    database components (tables, functions, sequences, types, views).
    """
    
    def __init__(self, db_session=None, config_path=None):
        """Initialize the migration manager with a database session."""
        self.session = db_session or get_sync_db()
        self.config = self._load_config(config_path)
        self.migration_history = self._load_migration_history()
        
    def migrate_up(self, component_type=None, version=None):
        """Apply migrations to reach the specified version."""
        pass
        
    def migrate_down(self, component_type=None, version=None):
        """Roll back migrations to the specified version."""
        pass
        
    def get_current_version(self, component_type=None):
        """Get the current database schema version."""
        pass
        
    def _execute_sql_file(self, file_path):
        """Execute SQL from a file."""
        pass
        
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

### 2. Component-Specific Migration Classes

Create specialized classes for each component type:

```python
class TableMigration(BaseMigration):
    """Handles table schema migrations."""
    component_type = "tables"
    
    def up(self, version=None):
        """Apply table migrations up to the specified version."""
        pass
        
    def down(self, version=None):
        """Roll back table migrations to the specified version."""
        pass

# Similar classes for functions, types, sequences, and views
```

### 3. Migration Configuration Schema

Create a YAML configuration file for migration settings:

```yaml
# migrations.yaml
database:
  default_schema: public
  migration_table: schema_migrations
  
components:
  - name: tables
    dependencies: [types, sequences]
    directory: sql/tables
    
  - name: functions 
    dependencies: [tables]
    directory: sql/functions
    
  - name: types
    dependencies: []
    directory: sql/types
    
  - name: sequences
    dependencies: []
    directory: sql/sequences
    
  - name: views
    dependencies: [tables, functions]
    directory: sql/views
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
    parser.add_argument('--component', choices=['all', 'tables', 'functions', 'types', 'sequences', 'views'],
                       default='all', help='Component type to migrate')
    parser.add_argument('--version', help='Target version to migrate to')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    manager = SqlMigrationManager(config_path=args.config)
    
    if args.direction == 'up':
        manager.migrate_up(args.component, args.version)
    else:
        manager.migrate_down(args.component, args.version)

if __name__ == '__main__':
    main()
```

## Implementation Timeline

1. Create migration configuration schema and loading logic
2. Implement core SqlMigrationManager class with file execution capabilities 
3. Create migration history table and tracking functionality
4. Implement component-specific migration handlers
5. Build CLI interface
6. Add testing and validation capabilities
7. Document usage and examples

## Conclusion

This migration manager will provide a structured approach to database schema management. It will enforce the proper dependency order when creating database components and provide a reliable way to roll back changes when needed. The tool will work with both local development environments and Google Cloud SQL production deployments.