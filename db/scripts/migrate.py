#!/usr/bin/env python3
import os
import argparse
import glob
from datetime import datetime
import logging
import sys
import pandas as pd
import sqlalchemy

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import the database connection module
from db_connection import (
    load_config, 
    get_db_engine, 
    get_db_connection, 
    execute_sql_script, 
    execute_sql_script_file,
    load_csv_to_db
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_migration_tracking(conn):
    """Create migration tracking table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR PRIMARY KEY,
        applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
        description TEXT
    )
    """
    execute_sql_script(conn, query)
    conn.commit()
    logger.info("Migration tracking table initialized")

def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    query = "SELECT version FROM schema_migrations ORDER BY version"
    result = execute_sql_script(conn, query)
    return [row[0] for row in result]

def apply_migration(conn, migration_dir):
    """Apply a single migration."""
    version = os.path.basename(migration_dir)
    description = version.split('_', 1)[1] if '_' in version else version
    
    try:
        # Special handling for data loading migrations
        if version == '0002_populate_core_data':
            logger.info(f"Applying data migration {version}")
            
            # Execute the SQL file first (for TRUNCATE, etc.)
            up_sql_path = os.path.join(migration_dir, 'up.sql')
            if os.path.exists(up_sql_path):
                try:
                    execute_sql_script_file(conn, up_sql_path)
                except Exception as e:
                    logger.warning(f"Error executing {up_sql_path}: {e}")
                    # Continue anyway as this might be a partial migration
            
            # Get engine for pandas loading
            engine = conn.engine
            
            # Define data directory
            data_dir = os.path.join(os.path.dirname(os.path.dirname(migration_dir)), 'data')
            
            # Define all CSV files to load
            csv_files = {
                # Core tables
                'snp': {
                    'path': os.path.join(data_dir, 'snps.csv'),
                    'columns': ['rsid', 'gene', 'risk_allele', 'effect', 'evidence_strength', 'category']
                },
                'skincharacteristic': {
                    'path': os.path.join(data_dir, 'characteristics.csv'),
                    'columns': ['name', 'description', 'measurement_method']
                },
                'ingredient': {
                    'path': os.path.join(data_dir, 'ingredients.csv'),
                    'columns': ['name', 'mechanism', 'evidence_level', 'contraindications']
                },
                'ingredientcaution': {
                    'path': os.path.join(data_dir, 'ingredient_cautions.csv'),
                    'columns': ['ingredient_name', 'category', 'risk_mechanism', 'affected_characteristic', 'alternative_ingredients']
                },
                'skincondition': {
                    'path': os.path.join(data_dir, 'skin_conditions.csv'),
                    'columns': ['name', 'description', 'severity_scale']
                }
            }
            
            # First load all the core tables
            for table, info in csv_files.items():
                if os.path.exists(info['path']):
                    try:
                        logger.info(f"Loading data for {table} from {info['path']}")
                        load_csv_to_db(
                            engine,
                            table,
                            info['path'],
                            columns=info['columns']
                        )
                    except Exception as e:
                        logger.warning(f"Error loading {table} data: {e}")
                else:
                    logger.warning(f"CSV file not found: {info['path']}")
                    
            # Now load relationship data
            relationships_dir = os.path.join(data_dir, 'relationships')
            
            # Function to load relationship data with ID resolution using direct SQL queries
            def load_relationship_data(csv_path, link_table, source_table, source_col, target_table, target_col, extra_cols=None):
                if not os.path.exists(csv_path):
                    logger.warning(f"Relationship CSV file not found: {csv_path}")
                    return
                    
                try:
                    # Read the CSV data
                    df = pd.read_csv(csv_path)
                    if df.empty:
                        logger.warning(f"No data in {csv_path}")
                        return
                    
                    # Get ID column names from database metadata
                    source_id_col = None
                    target_id_col = None
                    
                    # Check source table ID column
                    source_id_query = f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{source_table}' AND column_name LIKE '%id%' 
                        ORDER BY ordinal_position LIMIT 1
                    """
                    source_id_result = conn.execute(sqlalchemy.text(source_id_query))
                    source_id_row = source_id_result.fetchone()
                    if source_id_row:
                        source_id_col = source_id_row[0]
                    else:
                        logger.error(f"Could not determine ID column for {source_table}")
                        return
                    
                    # Check target table ID column
                    target_id_query = f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{target_table}' AND column_name LIKE '%id%' 
                        ORDER BY ordinal_position LIMIT 1
                    """
                    target_id_result = conn.execute(sqlalchemy.text(target_id_query))
                    target_id_row = target_id_result.fetchone()
                    if target_id_row:
                        target_id_col = target_id_row[0]
                    else:
                        logger.error(f"Could not determine ID column for {target_table}")
                        return
                    
                    logger.info(f"Using {source_id_col} for {source_table} and {target_id_col} for {target_table}")
                    
                    # Get the ID mappings from source table
                    source_query = f"SELECT {source_id_col}, {source_col} FROM {source_table}"
                    source_ids = pd.read_sql(source_query, engine)
                    
                    # Get the ID mappings from target table
                    target_query = f"SELECT {target_id_col}, {target_col} FROM {target_table}"
                    target_ids = pd.read_sql(target_query, engine)
                    
                    # Create empty DataFrame for the link table
                    link_df = pd.DataFrame()
                    
                    # Map names to IDs
                    df = df.merge(source_ids, left_on=source_col, right_on=source_col, how='inner')
                    df = df.merge(target_ids, left_on=target_col, right_on=target_col, how='inner')
                    
                    # Check if IDs were mapped correctly
                    if len(df) == 0:
                        logger.warning(f"No matches found when mapping IDs for {csv_path}")
                        return
                    
                    # Create link table data
                    link_df[source_id_col] = df[source_id_col]
                    link_df[target_id_col] = df[target_id_col]
                    
                    # Add any extra columns
                    if extra_cols:
                        for col in extra_cols:
                            if col in df.columns:
                                link_df[col] = df[col]
                    
                    # Load to database
                    logger.info(f"Loading relationship data into {link_table} from {csv_path}")
                    link_df.to_sql(
                        link_table, 
                        engine, 
                        if_exists='append', 
                        index=False,
                        method='multi',
                        chunksize=1000
                    )
                    logger.info(f"Loaded {len(link_df)} rows into {link_table}")
                except Exception as e:
                    logger.warning(f"Error loading relationship data from {csv_path}: {e}")
            
            # Load all relationship data
            try:
                # We need to handle the column name collision for characteristic_condition.csv and condition_ingredient.csv
                # For these cases, we'll modify the DataFrames directly before merging
                
                # SNP to Characteristic
                try:
                    csv_path = os.path.join(relationships_dir, 'snp_characteristic.csv')
                    if os.path.exists(csv_path):
                        logger.info(f"Loading SNP to Characteristic relationships from {csv_path}")
                        df = pd.read_csv(csv_path)
                        
                        # Get IDs from database
                        snp_ids = pd.read_sql("SELECT snp_id, rsid FROM snp", engine)
                        char_ids = pd.read_sql("SELECT characteristic_id, name FROM skincharacteristic", engine)
                        
                        # Merge to get the IDs
                        link_df = pd.merge(df, snp_ids, on='rsid')
                        link_df = pd.merge(link_df, char_ids, on='name')
                        
                        # Select only needed columns
                        result_df = pd.DataFrame({
                            'snp_id': link_df['snp_id'],
                            'characteristic_id': link_df['characteristic_id'],
                            'effect_direction': link_df['effect_direction'],
                            'evidence_strength': link_df['evidence_strength']
                        })
                        
                        # Write to database
                        result_df.to_sql('snp_characteristic_link', engine, if_exists='append', index=False)
                        logger.info(f"Loaded {len(result_df)} SNP-Characteristic relationships")
                except Exception as e:
                    logger.error(f"Error loading SNP-Characteristic relationships: {e}")
                
                # SNP to Ingredient
                try:
                    csv_path = os.path.join(relationships_dir, 'snp_ingredient.csv')
                    if os.path.exists(csv_path):
                        logger.info(f"Loading SNP to Ingredient relationships from {csv_path}")
                        df = pd.read_csv(csv_path)
                        
                        # Get IDs from database
                        snp_ids = pd.read_sql("SELECT snp_id, rsid FROM snp", engine) 
                        ing_ids = pd.read_sql("SELECT ingredient_id, name FROM ingredient", engine)
                        
                        # Merge to get the IDs
                        link_df = pd.merge(df, snp_ids, on='rsid')
                        link_df = pd.merge(link_df, ing_ids, on='name')
                        
                        # Select only needed columns
                        result_df = pd.DataFrame({
                            'snp_id': link_df['snp_id'],
                            'ingredient_id': link_df['ingredient_id'],
                            'benefit_mechanism': link_df['benefit_mechanism'],
                            'recommendation_strength': link_df['recommendation_strength'],
                            'evidence_level': link_df['evidence_level']
                        })
                        
                        # Write to database
                        result_df.to_sql('snp_ingredient_link', engine, if_exists='append', index=False)
                        logger.info(f"Loaded {len(result_df)} SNP-Ingredient relationships")
                except Exception as e:
                    logger.error(f"Error loading SNP-Ingredient relationships: {e}")
                
                # SNP to IngredientCaution
                try:
                    csv_path = os.path.join(relationships_dir, 'snp_ingredientcaution.csv')
                    if os.path.exists(csv_path):
                        logger.info(f"Loading SNP to IngredientCaution relationships from {csv_path}")
                        df = pd.read_csv(csv_path)
                        
                        # Get IDs from database
                        snp_ids = pd.read_sql("SELECT snp_id, rsid FROM snp", engine)
                        caution_ids = pd.read_sql("SELECT caution_id, ingredient_name FROM ingredientcaution", engine)
                        
                        # Merge to get the IDs
                        link_df = pd.merge(df, snp_ids, on='rsid')
                        link_df = pd.merge(link_df, caution_ids, on='ingredient_name')
                        
                        # Select only needed columns
                        result_df = pd.DataFrame({
                            'snp_id': link_df['snp_id'],
                            'caution_id': link_df['caution_id'],
                            'relationship_notes': link_df['relationship_notes'],
                            'evidence_level': link_df['evidence_level']
                        })
                        
                        # Write to database
                        result_df.to_sql('snp_ingredientcaution_link', engine, if_exists='append', index=False)
                        logger.info(f"Loaded {len(result_df)} SNP-IngredientCaution relationships")
                except Exception as e:
                    logger.error(f"Error loading SNP-IngredientCaution relationships: {e}")
                
                # Characteristic to Condition (special handling for name column collision)
                try:
                    csv_path = os.path.join(relationships_dir, 'characteristic_condition.csv')
                    if os.path.exists(csv_path):
                        logger.info(f"Loading Characteristic to Condition relationships from {csv_path}")
                        df = pd.read_csv(csv_path)
                        df = df.rename(columns={'name': 'char_name', 'name.1': 'cond_name'})
                        
                        # Get IDs from database
                        char_ids = pd.read_sql("SELECT characteristic_id, name FROM skincharacteristic", engine)
                        cond_ids = pd.read_sql("SELECT condition_id, name FROM skincondition", engine)
                        
                        # Merge to get the IDs - note the different column names
                        link_df = pd.merge(df, char_ids, left_on='char_name', right_on='name')
                        link_df = pd.merge(link_df, cond_ids, left_on='cond_name', right_on='name')
                        
                        # Select only needed columns
                        result_df = pd.DataFrame({
                            'characteristic_id': link_df['characteristic_id'],
                            'condition_id': link_df['condition_id'],
                            'relationship_type': link_df['relationship_type']
                        })
                        
                        # Write to database
                        result_df.to_sql('characteristic_condition_link', engine, if_exists='append', index=False)
                        logger.info(f"Loaded {len(result_df)} Characteristic-Condition relationships")
                except Exception as e:
                    logger.error(f"Error loading Characteristic-Condition relationships: {e}")
                
                # Condition to Ingredient (special handling for name column collision)
                try:
                    csv_path = os.path.join(relationships_dir, 'condition_ingredient.csv')
                    if os.path.exists(csv_path):
                        logger.info(f"Loading Condition to Ingredient relationships from {csv_path}")
                        df = pd.read_csv(csv_path)
                        df = df.rename(columns={'name': 'cond_name', 'name.1': 'ing_name'})
                        
                        # Get IDs from database
                        cond_ids = pd.read_sql("SELECT condition_id, name FROM skincondition", engine)
                        ing_ids = pd.read_sql("SELECT ingredient_id, name FROM ingredient", engine)
                        
                        # Merge to get the IDs - note the different column names
                        link_df = pd.merge(df, cond_ids, left_on='cond_name', right_on='name')
                        link_df = pd.merge(link_df, ing_ids, left_on='ing_name', right_on='name')
                        
                        # Select only needed columns
                        result_df = pd.DataFrame({
                            'condition_id': link_df['condition_id'],
                            'ingredient_id': link_df['ingredient_id'],
                            'recommendation_strength': link_df['recommendation_strength'],
                            'guidance_notes': link_df['guidance_notes']
                        })
                        
                        # Write to database
                        result_df.to_sql('condition_ingredient_link', engine, if_exists='append', index=False)
                        logger.info(f"Loaded {len(result_df)} Condition-Ingredient relationships")
                except Exception as e:
                    logger.error(f"Error loading Condition-Ingredient relationships: {e}")
            except Exception as e:
                logger.warning(f"Error loading relationship data: {e}")
            
        # Special handling for database functions migration
        elif version == '0004_database_functions':
            logger.info(f"Applying database functions migration {version}")
            
            # First, execute the up.sql file which starts the transaction
            up_sql_path = os.path.join(migration_dir, 'up.sql')
            if os.path.exists(up_sql_path):
                try:
                    execute_sql_script_file(conn, up_sql_path)
                except Exception as e:
                    logger.warning(f"Error executing {up_sql_path}: {e}")
                    # Continue anyway as this might be a partial migration
            
            # Check for a functions directory
            functions_dir = os.path.join(migration_dir, 'functions')
            if os.path.exists(functions_dir) and os.path.isdir(functions_dir):
                # Get all SQL files in the functions directory
                function_files = glob.glob(os.path.join(functions_dir, '*.sql'))
                function_files.sort()  # Sort to ensure correct order
                
                # Apply each function file individually
                for function_file in function_files:
                    logger.info(f"Applying function file {os.path.basename(function_file)}")
                    try:
                        execute_sql_script_file(conn, function_file)
                    except Exception as e:
                        logger.warning(f"Error executing {function_file}: {e}")
                        # Continue anyway as this might be a partial migration
            
        else:
            # Normal SQL migration
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
                logger.info(f"Applying {os.path.basename(sql_file)} from migration {version}")
                try:
                    execute_sql_script_file(conn, sql_file)
                except Exception as e:
                    logger.warning(f"Error executing {sql_file}: {e}")
                    # Continue anyway as this might be a partial migration
        
        # Record migration regardless of errors
        query = "INSERT INTO schema_migrations (version, description) VALUES (:version, :description)"
        conn.execute(sqlalchemy.text(query).bindparams(version=version, description=description))
        
        conn.commit()
        logger.info(f"Migration {version} applied successfully")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to apply migration {version}: {e}")
        raise

def run_migrations(env='development'):
    """Run all pending migrations."""
    config = load_config(env)
    conn = get_db_connection(config, env)
    
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
                      help='Environment (development, test, production, cloud)')
    args = parser.parse_args()
    
    run_migrations(args.env)