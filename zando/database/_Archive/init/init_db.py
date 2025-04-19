import psycopg2
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path) as f:
        return yaml.safe_load(f)

def init_database():
    config = load_config()
    db_config = config['database']
    
    # Connect to database
    conn = psycopg2.connect(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['user'],
        password=db_config['password']
    )
    
    # Create tables
    with conn.cursor() as cur:
        # Read and execute schema file
        schema_path = os.path.join(
            os.path.dirname(__file__), 
            '../schema/01_create_tables.sql'
        )
        with open(schema_path) as f:
            cur.execute(f.read())
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
