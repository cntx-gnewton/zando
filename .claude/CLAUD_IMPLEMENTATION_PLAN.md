# Zando Database Optimization Implementation Plan

This document outlines a comprehensive plan for optimizing the database initialization, schema design, and data management for the Zando genomic analysis platform.

## Goals

1. Improve database initialization and migration processes
2. Move from hard-coded data to CSV-based data loading
3. Enhance schema design with proper constraints and indexes
4. Create a robust system for managing database changes
5. Implement proper documentation

## Phase 1: Restructure and Initial Improvements (Days 1-2)

### 1.1: Create New Directory Structure

```
/db
  /migrations           # Version-numbered migration directories
    /0001_initial_schema
      schema.sql        # Table definitions
      functions.sql     # Function definitions
      types.sql         # Custom type definitions
    /0002_populate_core_data
      up.sql            # Apply migration
      down.sql          # Rollback migration
  /data                 # CSV files for all reference data
    snps.csv
    characteristics.csv
    ingredients.csv
    ingredient_cautions.csv
    relationships/      # CSV files for relationship tables
      snp_characteristic_links.csv
      characteristic_condition_links.csv
      snp_ingredient_links.csv
  /scripts              # Database management scripts
    init_db.py          # Database initialization
    migrate.py          # Migration management
  config.yaml           # Configuration for different environments
  README.md             # Documentation
```

### 1.2: Convert Hard-coded Data to CSV Files

1. **Extract Current Data**
   - Extract SNP data from `03_populate_snps.sql` to `snps.csv` (use existing snp.csv as base)
   - Extract characteristics data from `04_populate_characteristics.sql` to `characteristics.csv`
   - Extract ingredients data from `08_populate_ingredients.sql` to `ingredients.csv`
   - Extract ingredient cautions from `09_ingredient_cautions.sql` to `ingredient_cautions.csv`
   - Extract relationship data to respective CSV files in `/db/data/relationships/`

2. **Standard CSV Format**
   - Ensure all CSV files have proper headers matching table columns
   - Add proper quotation for text fields with commas or special characters
   - Document CSV format requirements in README.md

### 1.3: Create Basic Migration Scripts

1. **Initial Schema Migration**
   - Create `0001_initial_schema/schema.sql` with all table definitions 
   - Create `0001_initial_schema/types.sql` with all custom type definitions
   - Create `0001_initial_schema/functions.sql` with all database functions

2. **Data Migration**
   - Create `0002_populate_core_data/up.sql` with COPY commands for all data tables
   - Create `0002_populate_core_data/down.sql` with TRUNCATE commands for rollback

## Phase 2: Enhanced Data Loading and Migration System (Days 3-5)

### 2.1: Develop Migration Manager Script

Create a Python script (`db/scripts/migrate.py`) that:

```python
import psycopg2
import yaml
import os
import argparse
import glob
from datetime import datetime

def load_config(env='development'):
    """Load configuration for specified environment."""
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)
        return config.get(env, config.get('development'))

def get_connection(config):
    """Establish database connection."""
    return psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

def initialize_migration_tracking(conn):
    """Create migration tracking table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR PRIMARY KEY,
            applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
            description TEXT
        )
        """)
    conn.commit()

def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version")
        return [row[0] for row in cur.fetchall()]

def apply_migration(conn, migration_dir):
    """Apply a single migration."""
    version = os.path.basename(migration_dir)
    description = version.split('_', 1)[1] if '_' in version else version
    
    # Check for up.sql or specific SQL files
    up_sql_path = os.path.join(migration_dir, 'up.sql')
    if os.path.exists(up_sql_path):
        sql_files = [up_sql_path]
    else:
        # Look for all .sql files except down.sql
        sql_files = [f for f in glob.glob(os.path.join(migration_dir, '*.sql')) 
                    if not f.endswith('down.sql')]
        sql_files.sort()
    
    # Apply each SQL file
    for sql_file in sql_files:
        with open(sql_file) as f:
            sql = f.read()
            
        print(f"Applying {os.path.basename(sql_file)} from migration {version}")
        with conn.cursor() as cur:
            cur.execute(sql)
    
    # Record migration
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
            (version, description)
        )
    
    conn.commit()
    print(f"Migration {version} applied successfully")

def run_migrations(env='development'):
    """Run all pending migrations."""
    config = load_config(env)
    conn = get_connection(config)
    
    try:
        # Ensure migration tracking is set up
        initialize_migration_tracking(conn)
        
        # Get applied migrations
        applied = get_applied_migrations(conn)
        
        # Find all migration directories
        migrations_path = os.path.join(os.path.dirname(__file__), '../migrations')
        migration_dirs = sorted(glob.glob(os.path.join(migrations_path, '*')))
        
        # Apply pending migrations
        for migration_dir in migration_dirs:
            version = os.path.basename(migration_dir)
            if version not in applied:
                apply_migration(conn, migration_dir)
    
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database migration manager')
    parser.add_argument('--env', default='development', 
                       help='Environment (development, test, production)')
    args = parser.parse_args()
    
    run_migrations(args.env)
```

### 2.2: Implement CSV Data Loading Utility

Create a Python function for loading CSV data:

```python
def load_csv_data(conn, table_name, csv_path, columns=None):
    """Load data from CSV into specified table."""
    with conn.cursor() as cur:
        # Build COPY command
        columns_clause = f"({','.join(columns)})" if columns else ""
        copy_cmd = f"COPY {table_name} {columns_clause} FROM STDIN WITH CSV HEADER"
        
        # Execute COPY with file content
        with open(csv_path, 'r') as f:
            cur.copy_expert(copy_cmd, f)
    
    conn.commit()
    print(f"Loaded data into {table_name} from {csv_path}")
```

### 2.3: Create Multi-Environment Configuration

```yaml
# config.yaml
development:
  host: localhost
  port: 5432
  database: zando_dev
  user: zando_user
  password: dev_password
  
test:
  host: localhost
  port: 5432
  database: zando_test
  user: zando_user
  password: test_password
  
production:
  host: ${DB_HOST}
  port: ${DB_PORT}
  database: ${DB_NAME}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
```

## Phase 3: Schema Enhancements and Indexing (Days 6-7)

### 3.1: Improve Schema with Constraints and Types

Create a new migration (`0003_schema_enhancements/up.sql`):

```sql
BEGIN;

-- Create enum types for consistent values
CREATE TYPE evidence_level_enum AS ENUM ('Strong', 'Moderate', 'Weak');
CREATE TYPE effect_direction_enum AS ENUM ('Increases', 'Decreases', 'Modulates');
CREATE TYPE recommendation_strength_enum AS ENUM ('First-line', 'Second-line', 'Adjuvant');

-- Convert columns to use enum types
ALTER TABLE snp 
ALTER COLUMN evidence_strength TYPE evidence_level_enum 
USING evidence_strength::evidence_level_enum;

ALTER TABLE ingredient 
ALTER COLUMN evidence_level TYPE evidence_level_enum 
USING evidence_level::evidence_level_enum;

ALTER TABLE snp_characteristic_link
ALTER COLUMN effect_direction TYPE effect_direction_enum
USING effect_direction::effect_direction_enum;

ALTER TABLE condition_ingredient_link
ALTER COLUMN recommendation_strength TYPE recommendation_strength_enum
USING recommendation_strength::recommendation_strength_enum;

COMMIT;
```

### 3.2: Add Performance Indexes

Create a new migration (`0004_add_indexes/up.sql`):

```sql
BEGIN;

-- Add indexes to SNP table
CREATE INDEX IF NOT EXISTS idx_snp_rsid ON snp(rsid);
CREATE INDEX IF NOT EXISTS idx_snp_gene ON snp(gene);
CREATE INDEX IF NOT EXISTS idx_snp_category ON snp(category);
CREATE INDEX IF NOT EXISTS idx_snp_evidence ON snp(evidence_strength);

-- Add indexes to characteristics
CREATE INDEX IF NOT EXISTS idx_characteristic_name ON skincharacteristic(name);

-- Add indexes to ingredients
CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredient(name);
CREATE INDEX IF NOT EXISTS idx_ingredient_evidence ON ingredient(evidence_level);

-- Add compound indexes to junction tables
CREATE INDEX IF NOT EXISTS idx_snp_char_link_snp ON snp_characteristic_link(snp_id);
CREATE INDEX IF NOT EXISTS idx_snp_char_link_char ON snp_characteristic_link(characteristic_id);

CREATE INDEX IF NOT EXISTS idx_char_cond_link_char ON characteristic_condition_link(characteristic_id);
CREATE INDEX IF NOT EXISTS idx_char_cond_link_cond ON characteristic_condition_link(condition_id);

COMMIT;
```

### 3.3: Add Table and Column Comments

Create a new migration (`0005_add_documentation/up.sql`):

```sql
BEGIN;

-- Add comments to core tables
COMMENT ON TABLE snp IS 'Single Nucleotide Polymorphisms (genetic variants) that affect skin characteristics';
COMMENT ON COLUMN snp.rsid IS 'Reference SNP ID (unique identifier from dbSNP database)';
COMMENT ON COLUMN snp.gene IS 'Gene symbol associated with this SNP';
COMMENT ON COLUMN snp.risk_allele IS 'Allele associated with the genetic effect';
COMMENT ON COLUMN snp.effect IS 'Description of the genetic effect on skin';
COMMENT ON COLUMN snp.evidence_strength IS 'Scientific evidence strength (Strong, Moderate, Weak)';
COMMENT ON COLUMN snp.category IS 'Functional category of the genetic variant';

COMMENT ON TABLE skincharacteristic IS 'Skin traits or properties that can be affected by genetic variants';
COMMENT ON COLUMN skincharacteristic.name IS 'Name of the skin characteristic';
COMMENT ON COLUMN skincharacteristic.description IS 'Detailed description of the characteristic';
COMMENT ON COLUMN skincharacteristic.measurement_method IS 'How this characteristic can be measured or assessed';

COMMENT ON TABLE ingredient IS 'Skincare ingredients that may be beneficial based on genetic profile';
COMMENT ON COLUMN ingredient.name IS 'Name of the ingredient';
COMMENT ON COLUMN ingredient.mechanism IS 'How the ingredient works on skin';
COMMENT ON COLUMN ingredient.evidence_level IS 'Scientific evidence strength for ingredient efficacy';
COMMENT ON COLUMN ingredient.contraindications IS 'Any warnings or contraindications for this ingredient';

-- Add comments to junction tables
COMMENT ON TABLE snp_characteristic_link IS 'Links between genetic variants and the skin characteristics they affect';
COMMENT ON COLUMN snp_characteristic_link.effect_direction IS 'How the SNP affects the characteristic (Increases, Decreases, Modulates)';
COMMENT ON COLUMN snp_characteristic_link.evidence_strength IS 'Scientific evidence strength for this specific relationship';

-- Add more comments for other tables...

COMMIT;
```

## Phase 4: Documentation and Data Dictionary (Days 8-10)

### 4.1: Create Data Dictionary Generator

```python
def generate_data_dictionary(conn, output_file='data_dictionary.md'):
    """Generate a comprehensive data dictionary markdown file."""
    with open(output_file, 'w') as f:
        # Document tables
        f.write("# Zando Database Dictionary\n\n")
        
        # Get list of tables
        with conn.cursor() as cur:
            cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
        
        for table in tables:
            f.write(f"## {table}\n\n")
            
            # Get table description
            with conn.cursor() as cur:
                cur.execute(f"SELECT obj_description('{table}'::regclass)")
                description = cur.fetchone()[0]
                if description:
                    f.write(f"{description}\n\n")
            
            # Get column info
            with conn.cursor() as cur:
                cur.execute(f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    pgd.description
                FROM information_schema.columns c
                LEFT JOIN pg_description pgd ON 
                    pgd.objoid = ('{table}'::regclass)::oid AND 
                    pgd.objsubid = c.ordinal_position
                WHERE table_schema = 'public' AND table_name = '{table}'
                ORDER BY ordinal_position
                """)
                
                f.write("| Column | Type | Nullable | Default | Description |\n")
                f.write("|--------|------|----------|---------|-------------|\n")
                
                for col in cur.fetchall():
                    f.write(f"| {col[0]} | {col[1]} | {col[2]} | {col[3] or ''} | {col[4] or ''} |\n")
            
            f.write("\n\n")
```

### 4.2: Create Comprehensive README

Create a detailed `db/README.md` with:

1. **Database Overview**
   - Schema diagram or description
   - Core tables and their relationships
   - Data lifecycle

2. **Setup Instructions**
   - How to initialize the database
   - How to run migrations
   - Environment configuration

3. **Development Guidelines**
   - How to add new migrations
   - CSV format requirements
   - Coding standards for SQL

4. **Data Management**
   - How to update reference data
   - Data validation procedures
   - Backup and restore procedures

### 4.3: Create Database Schema Diagram

Use a tool like `pg_dump` with the `-s` option to extract the schema, then visualize it with a tool like SchemaSpy, pgAdmin, or DbVisualizer.

## Phase 5: Testing and Validation (Days 11-14)

### 5.1: Create Database Unit Tests

```python
import unittest
import psycopg2
import yaml
import os

class DatabaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load test config
        config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
        with open(config_path) as f:
            config = yaml.safe_load(f).get('test')
        
        # Connect to test database
        cls.conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
    
    def test_schema_integrity(self):
        """Test database schema integrity."""
        # Check if all required tables exist
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cur.fetchall()]
            
            required_tables = ['snp', 'skincharacteristic', 'ingredient']
            for table in required_tables:
                self.assertIn(table, tables)
    
    def test_data_integrity(self):
        """Test core data integrity."""
        # Check if core data is loaded
        with self.conn.cursor() as cur:
            # Check SNP table
            cur.execute("SELECT COUNT(*) FROM snp")
            snp_count = cur.fetchone()[0]
            self.assertGreater(snp_count, 0)
            
            # Check unique constraints
            cur.execute("SELECT count(*), count(distinct rsid) FROM snp")
            total, distinct = cur.fetchone()
            self.assertEqual(total, distinct)
            
    def test_relationships(self):
        """Test relationship integrity."""
        with self.conn.cursor() as cur:
            # Check if there are no orphan records in relationship tables
            cur.execute("""
            SELECT COUNT(*) FROM snp_characteristic_link scl
            LEFT JOIN snp s ON scl.snp_id = s.snp_id
            WHERE s.snp_id IS NULL
            """)
            orphans = cur.fetchone()[0]
            self.assertEqual(orphans, 0)

if __name__ == '__main__':
    unittest.main()
```

### 5.2: Create Data Validation Script

```python
def validate_csv_data(csv_file, schema):
    """
    Validate CSV data against a schema definition.
    
    Args:
        csv_file (str): Path to CSV file
        schema (dict): Schema definition with column types and constraints
        
    Returns:
        list: List of validation errors or empty list if valid
    """
    import csv
    import re
    
    errors = []
    
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        
        # Validate header
        required_fields = schema.keys()
        missing_fields = [field for field in required_fields 
                          if field not in reader.fieldnames]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate rows
        for i, row in enumerate(reader, start=2):  # Start at line 2 (after header)
            for field, constraints in schema.items():
                if field not in row:
                    continue
                    
                value = row[field]
                
                # Check required
                if constraints.get('required', False) and not value:
                    errors.append(f"Line {i}: Required field '{field}' is empty")
                
                # Check type
                if value and 'type' in constraints:
                    field_type = constraints['type']
                    
                    if field_type == 'integer':
                        if not value.isdigit():
                            errors.append(f"Line {i}: Field '{field}' must be an integer")
                            
                    elif field_type == 'decimal':
                        try:
                            float(value)
                        except ValueError:
                            errors.append(f"Line {i}: Field '{field}' must be a number")
                            
                    elif field_type == 'enum':
                        allowed = constraints.get('allowed', [])
                        if value not in allowed:
                            errors.append(f"Line {i}: Field '{field}' must be one of: {', '.join(allowed)}")
                
                # Check pattern
                if value and 'pattern' in constraints:
                    pattern = constraints['pattern']
                    if not re.match(pattern, value):
                        errors.append(f"Line {i}: Field '{field}' does not match pattern {pattern}")
                        
    return errors

# Example schema for SNP data
snp_schema = {
    'rsid': {
        'required': True,
        'pattern': r'^rs\d+$',
        'description': 'Reference SNP ID'
    },
    'gene': {
        'required': True,
        'description': 'Gene symbol'
    },
    'risk_allele': {
        'required': True,
        'pattern': r'^[ATGC]$',
        'description': 'Risk allele (A, T, G, C)'
    },
    'effect': {
        'required': True,
        'description': 'Description of effect'
    },
    'evidence_strength': {
        'required': True,
        'type': 'enum',
        'allowed': ['Strong', 'Moderate', 'Weak'],
        'description': 'Evidence strength'
    },
    'category': {
        'required': True,
        'description': 'Functional category'
    }
}

# Validate SNP data
errors = validate_csv_data('db/data/snps.csv', snp_schema)
if errors:
    for error in errors:
        print(error)
else:
    print("SNP data is valid")
```

### 5.3: Create Data Integrity Check Script

```python
def check_database_integrity(conn):
    """Check database integrity and report issues."""
    issues = []
    
    with conn.cursor() as cur:
        # Check for orphaned records in relationship tables
        cur.execute("""
        SELECT 'snp_characteristic_link' as table_name, COUNT(*) as orphans
        FROM snp_characteristic_link scl
        LEFT JOIN snp s ON scl.snp_id = s.snp_id
        WHERE s.snp_id IS NULL
        
        UNION ALL
        
        SELECT 'snp_characteristic_link' as table_name, COUNT(*) as orphans
        FROM snp_characteristic_link scl
        LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
        WHERE sc.characteristic_id IS NULL
        
        UNION ALL
        
        -- Add more relationship checks...
        """)
        
        for row in cur.fetchall():
            if row[1] > 0:
                issues.append(f"Found {row[1]} orphaned records in {row[0]}")
        
        # Check for duplicate rsids
        cur.execute("""
        SELECT rsid, COUNT(*) 
        FROM snp 
        GROUP BY rsid 
        HAVING COUNT(*) > 1
        """)
        
        for row in cur.fetchall():
            issues.append(f"Found duplicate rsid: {row[0]} ({row[1]} occurrences)")
        
        # Check for missing required data
        cur.execute("""
        SELECT 'SNPs with empty gene' as issue, COUNT(*) 
        FROM snp 
        WHERE gene IS NULL OR gene = ''
        
        UNION ALL
        
        SELECT 'SNPs with empty category' as issue, COUNT(*) 
        FROM snp 
        WHERE category IS NULL OR category = ''
        
        -- Add more data quality checks...
        """)
        
        for row in cur.fetchall():
            if row[1] > 0:
                issues.append(f"{row[0]}: {row[1]} records")
    
    return issues
```

## Phase 6: Integration and Deployment (Days 15-16)

### 6.1: Create FastAPI Integration

Update the FastAPI backend to use the new database schema and migration system:

1. **Update Database Connection**
   - Use the shared configuration system
   - Implement proper pooling

2. **Create Database Initialization Script**
   - Add script to initialize database on application startup
   - Check migration status on startup

3. **Update Deployment Documentation**
   - Document database setup steps for different environments
   - Include backup and restore procedures

### 6.2: Create Database Management Commands

```python
# db/scripts/manage.py

import argparse
import os
import sys
import psycopg2
import yaml

# Import utility functions
from migrate import run_migrations, load_config, get_connection
from data_dictionary import generate_data_dictionary
from integrity_check import check_database_integrity

def init_db(args):
    """Initialize the database from scratch."""
    config = load_config(args.env)
    
    # Connect to PostgreSQL server (not the specific database)
    admin_conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database='postgres',  # Connect to default database
        user=config['user'],
        password=config['password']
    )
    admin_conn.autocommit = True
    
    try:
        # Create database if it doesn't exist
        with admin_conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'")
            db_exists = cur.fetchone()
            
            if not db_exists:
                print(f"Creating database {config['database']}...")
                cur.execute(f"CREATE DATABASE {config['database']}")
                print(f"Database {config['database']} created.")
            else:
                print(f"Database {config['database']} already exists.")
    finally:
        admin_conn.close()
    
    # Run all migrations
    run_migrations(args.env)

def reset_db(args):
    """Reset the database (drop and recreate)."""
    config = load_config(args.env)
    
    if args.env == 'production' and not args.force:
        print("Refusing to reset production database without --force flag.")
        return
    
    # Connect to PostgreSQL server (not the specific database)
    admin_conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        database='postgres',  # Connect to default database
        user=config['user'],
        password=config['password']
    )
    admin_conn.autocommit = True
    
    try:
        # Drop database if it exists
        with admin_conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'")
            db_exists = cur.fetchone()
            
            if db_exists:
                print(f"Dropping database {config['database']}...")
                
                # Terminate all connections
                cur.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{config['database']}'
                AND pid <> pg_backend_pid()
                """)
                
                cur.execute(f"DROP DATABASE {config['database']}")
                print(f"Database {config['database']} dropped.")
            
            # Create new database
            print(f"Creating database {config['database']}...")
            cur.execute(f"CREATE DATABASE {config['database']}")
            print(f"Database {config['database']} created.")
    finally:
        admin_conn.close()
    
    # Run all migrations
    run_migrations(args.env)

def check_db(args):
    """Check database integrity."""
    config = load_config(args.env)
    conn = get_connection(config)
    
    try:
        issues = check_database_integrity(conn)
        
        if issues:
            print("Database integrity issues found:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("Database integrity check passed!")
    finally:
        conn.close()

def doc_db(args):
    """Generate database documentation."""
    config = load_config(args.env)
    conn = get_connection(config)
    
    try:
        print(f"Generating data dictionary to {args.output}...")
        generate_data_dictionary(conn, args.output)
        print(f"Data dictionary generated successfully!")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database management utility")
    parser.add_argument('--env', default='development',
                       help='Environment (development, test, production)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    init_parser.set_defaults(func=init_db)
    
    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database (drop and recreate)')
    reset_parser.add_argument('--force', action='store_true', help='Force reset in production')
    reset_parser.set_defaults(func=reset_db)
    
    # migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    migrate_parser.set_defaults(func=lambda args: run_migrations(args.env))
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check database integrity')
    check_parser.set_defaults(func=check_db)
    
    # doc command
    doc_parser = subparsers.add_parser('doc', help='Generate database documentation')
    doc_parser.add_argument('--output', default='data_dictionary.md', help='Output file path')
    doc_parser.set_defaults(func=doc_db)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)
```

## Summary Timeline

| Phase | Description | Days | Deliverables |
|-------|-------------|------|--------------|
| 1 | Restructure and Initial Improvements | 1-2 | Directory structure, CSV files, Basic scripts |
| 2 | Enhanced Data Loading and Migration | 3-5 | Migration manager, CSV loading utility, Config system |
| 3 | Schema Enhancements and Indexing | 6-7 | Improved constraints, Performance indexes, Documentation |
| 4 | Documentation and Data Dictionary | 8-10 | Data dictionary generator, README, Schema diagram |
| 5 | Testing and Validation | 11-14 | Unit tests, Data validation, Integrity checks |
| 6 | Integration and Deployment | 15-16 | API integration, Management commands |

## Expected Outcomes

1. **More Maintainable Database**
   - Proper migration tracking
   - Version-controlled schema changes
   - Documented database structure

2. **Improved Data Management**
   - CSV-based data loading for easier updates
   - Data validation to ensure integrity
   - Clear separation of schema and data

3. **Better Performance**
   - Optimized indexes for common queries
   - Proper constraints for data integrity
   - Efficient COPY operations for bulk loading

4. **Enhanced Developer Experience**
   - Simplified database setup
   - Clear documentation
   - Comprehensive management commands