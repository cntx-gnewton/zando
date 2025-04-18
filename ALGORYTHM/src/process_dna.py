#!/usr/bin/env python3
import sys
import json
import os
import time
import logging
import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd
import markdown
from io import StringIO
# load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d',
    handlers=[
        logging.StreamHandler()
    ]
)
logger.setLevel(logging.DEBUG)

# Cache settings
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
CACHE_EXPIRY = timedelta(days=7)  # Cache files expire after 7 days

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

def compute_file_hash(file_content):
    """
    Compute a hash of the file content for cache lookup.
    
    Args:
        file_content: The content of the DNA file
        
    Returns:
        str: A hex digest hash of the content
    """
    hash_obj = hashlib.sha256(file_content.encode('utf-8') if isinstance(file_content, str) else file_content)
    return hash_obj.hexdigest()

def get_cache_path(file_hash, format_type='json'):
    """
    Get the path to a cache file for the given hash.
    
    Args:
        file_hash: Hash of the file content
        format_type: Type of cache file ('json', 'pdf', 'md')
        
    Returns:
        Path: Path object for the cache file
    """
    return Path(CACHE_DIR) / f"{file_hash}.{format_type}"

def save_to_cache(data, file_hash, format_type='json'):
    """
    Save data to the cache.
    
    Args:
        data: Data to cache (dict for 'json', bytes for 'pdf'/'md')
        file_hash: Hash of the file content
        format_type: Type of data being cached ('json', 'pdf', 'md')
    """
    cache_path = get_cache_path(file_hash, format_type)
    
    if format_type == 'json':
        # Save metadata with the cache
        cache_data = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'hash': file_hash
        }
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
    else:
        # Binary data (PDF, etc.)
        with open(cache_path, 'wb') as f:
            f.write(data)
    
    logger.info(f"Saved {format_type} cache file: {cache_path}")

def load_from_cache(file_hash, format_type='json'):
    """
    Load data from the cache if available and not expired.
    
    Args:
        file_hash: Hash of the file content
        format_type: Type of data to load ('json', 'pdf', 'md')
        
    Returns:
        The cached data if available and not expired, None otherwise
    """
    cache_path = get_cache_path(file_hash, format_type)
    
    if not cache_path.exists():
        return None
        
    # Check if cache is expired
    file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
    if file_age > CACHE_EXPIRY:
        logger.info(f"Cache expired ({file_age.days} days old): {cache_path}")
        cache_path.unlink(missing_ok=True)
        return None
    
    if format_type == 'json':
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            logger.info(f"Loaded cache from {cache_path}, created at {cache_data['timestamp']}")
            return cache_data['data']
        except (pickle.PickleError, KeyError, EOFError) as e:
            logger.warning(f"Error loading cache: {e}")
            cache_path.unlink(missing_ok=True)
            return None
    else:
        # Binary data (PDF, etc.)
        try:
            with open(cache_path, 'rb') as f:
                data = f.read()
            logger.info(f"Loaded {format_type} from cache: {cache_path}")
            return data
        except IOError as e:
            logger.warning(f"Error loading {format_type} cache: {e}")
            cache_path.unlink(missing_ok=True)
            return None

# logger.info(f"{os.environ['INSTANCE_CONNECTION_NAME']}, {os.environ['DB_USER']}, {os.environ['DB_PASS']}, {os.environ['DB_NAME']}")

def verify_and_read_txt(filepath):
    # Check if the file is a .txt file
    # if not filepath.endswith('.txt'):
    #     raise ValueError(f"The file {filepath} is not a .txt file")

    # Check if the file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError("The file does not exist")

    # Define possible sets of valid columns
    valid_columns_set1 = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
    valid_columns_set2 = ['rsid', 'chromosome', 'position', 'genotype']

    # Read the first 100 lines of the file
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            if i >= 100:
                break
            # Check if all valid columns from set 1 are in the line
            if all(column in line for column in valid_columns_set1):
                return valid_columns_set1
            # Check if all valid columns from set 2 are in the line
            if all(column in line for column in valid_columns_set2):
                return valid_columns_set2

    return []

def compute_file_hash_from_path(filepath):
    """
    Compute a hash of a file for cache lookup.
    
    Args:
        filepath: Path to the file
        
    Returns:
        str: A hex digest hash of the file content
    """
    hash_obj = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def read_dna_file(filepath, use_cache=True):
    """
    Reads and parses a DNA file, with optional caching.
    
    Args:
        filepath: Path to the DNA file
        use_cache: Whether to use/update cache (default: True)
        
    Returns:
        List of dictionaries with SNP data
    """
    # Check for cached version if caching is enabled
    if use_cache:
        file_hash = compute_file_hash_from_path(filepath)
        cached_data = load_from_cache(file_hash)
        if cached_data is not None:
            logger.info(f"Using cached SNP data for {filepath}")
            return cached_data
    
    # No cache hit or caching disabled, parse the file
    logger.info(f"Parsing DNA file: {filepath}")
    start_time = time.time()
    
    columns = verify_and_read_txt(filepath)
    if not columns:
        raise ValueError("The file does not contain the expected columns")

    # Read the data into a DataFrame
    df = pd.read_csv(filepath, sep='\t', comment='#', names=columns, dtype=str)

    # If the file contains a genotype column, split it into allele1 and allele2
    if 'genotype' in df.columns:
        df[['allele1', 'allele2']] = df['genotype'].apply(lambda x: pd.Series(list(x)))
        df.drop(columns=['genotype'], inplace=True)
    
    # Convert to records
    parsed_data = df.to_dict(orient='records')
    
    elapsed_time = time.time() - start_time
    logger.info(f"Parsed {len(parsed_data)} SNP records from {filepath} in {elapsed_time:.2f}s")
    
    # Cache the parsed data if caching is enabled
    if use_cache:
        file_hash = compute_file_hash_from_path(filepath)
        save_to_cache(parsed_data, file_hash)
        logger.info(f"Cached parsed SNP data for {filepath}")
    
    return parsed_data
# def read_dna_file(file_path):
#     """
#     Reads an AncestryDNA raw data .txt file and extracts SNP records.
#     Skips header lines (#) and the column header.
#     Returns a list of dicts with keys: rsid, chromosome, position, allele1, allele2.
#     """
#     snps = []
#     with open(file_path, 'r') as file:
#         for line in file:
#             line = line.strip()
#             # Skip comments and empty lines
#             if line.startswith("#") or not line:
#                 continue
#             # Skip the header row if present
#             if line.startswith("rsid"):
#                 continue

#             fields = line.split("\t")
#             if len(fields) >= 5:
#                 rsid, chromosome, position, allele1, allele2 = fields[:5]
#                 snps.append({
#                     'rsid': rsid,
#                     'chromosome': chromosome,
#                     'position': position,
#                     'allele1': allele1,
#                     'allele2': allele2
#                 })
#     return snps

# Global connection pool
_engine = None

def get_db_engine() -> sqlalchemy.engine.base.Engine:
    """
    Returns a global SQLAlchemy engine instance with connection pooling.
    
    This creates a singleton engine that can be reused across requests,
    improving performance by avoiding repeated connection establishment.
    
    Returns:
        SQLAlchemy engine with connection pooling
    """
    global _engine
    
    if _engine is not None:
        # Return existing engine if already created
        return _engine
    
    # Create new engine if none exists
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    db_user = os.environ["DB_USER"]
    db_pass = os.environ["DB_PASS"]
    db_name = os.environ["DB_NAME"]
    
    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC
    
    connector = Connector(refresh_strategy="LAZY")
    
    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn
    
    # Configure pooling parameters for better performance
    _engine = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # Pool settings
        pool_size=5,               # Default number of connections to maintain
        max_overflow=10,           # Allow up to 10 additional connections on high load
        pool_timeout=30,           # Wait up to 30 seconds for a connection
        pool_recycle=1800,         # Recycle connections after 30 minutes
        pool_pre_ping=True         # Check connection viability before using
    )
    
    logger.info("Database connection pool initialized")
    return _engine

def connect_to_database() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.
    
    Uses the Cloud SQL Python Connector package with connection pooling.
    
    Returns:
        SQLAlchemy engine with connection pooling
    """
    return get_db_engine()


def load_snp_table(conn):
    """
    Loads the SNP table into a pandas DataFrame.
    Legacy method - prefer using get_batch_snp_details for better performance.
    """
    query = "SELECT * FROM snp"
    df = pd.read_sql(query, conn)
    logger.debug(f"Loaded {len(df)} SNP records from the database.")
    return df


def get_batch_snp_details(conn, rsids):
    """
    Retrieves SNP details for multiple rsids in a single database query.
    
    Args:
        conn: Database connection
        rsids: List of rsid values to retrieve
        
    Returns:
        Dictionary mapping rsids to their details
    """
    if not rsids:
        return {}
    
    logger.info(f"Batch fetching {len(rsids)} SNP records")
    
    query = """
        SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category 
        FROM snp
        WHERE rsid = ANY(:rsids)
    """
    
    results = conn.execute(sqlalchemy.text(query), {'rsids': rsids}).fetchall()
    
    # Convert to dictionary for fast lookup
    snp_details = {}
    logging.info(f'Fetched {len(results)} SNP records {results[:15]}')
    
    for row in results:
        # Handle tuple results (index-based access)
        # Index positions: 0=snp_id, 1=rsid, 2=gene, 3=risk_allele, 4=effect, 5=evidence_strength, 6=category
        rsid = row[1]  # rsid is at index 1
        snp_details[rsid] = {
            'snp_id': row[0],
            'gene': row[2],
            'risk_allele': row[3],
            'effect': row[4],
            'evidence_strength': row[5],
            'category': row[6]
        }
    
    logger.info(f"Found {len(snp_details)} matching SNPs in database")
    return snp_details


def get_snp_details(df, rsid):
    """
    Retrieves SNP details from the pandas DataFrame using the provided rsid.
    Legacy method - prefer using get_batch_snp_details for better performance.
    """
    logging.debug(f'Fetching {rsid}')
    result = df[df['rsid'] == rsid]
    if not result.empty:
        row = result.iloc[0]
        return {
            'snp_id': row['snp_id'],
            'gene': row['gene'],
            'risk_allele': row['risk_allele'],
            'effect': row['effect'],
            'evidence_strength': row['evidence_strength'],
            'category': row['category']
        }
    return None

# def get_snp_details(conn, rsid):
    # """
    # Retrieves SNP details from the 'snp' table using the provided rsid.
    # """
    # query = """
    #     SELECT snp_id, gene, risk_allele, effect, evidence_strength, category 
    #     FROM snp
    #     WHERE rsid = :rsid
    # """
    # result = conn.execute(sqlalchemy.text(query), {'rsid': rsid}).fetchone()
    # if result:
    #     logger.info(f"SNP with rsid {rsid} not found in the database.")
    #     return {
    #         'snp_id': result['snp_id'],
    #         'gene': result['gene'],
    #         'risk_allele': result['risk_allele'],
    #         'effect': result['effect'],
    #         'evidence_strength': result['evidence_strength'],
    #         'category': result['category']
    #     }
    # else:
    #     # Return None if SNP not found
    #     return None

def get_related_skin_characteristics(conn, snp_id):
    """
    Fetches any related skin characteristics via SNP_Characteristic_Link.
    Legacy method - prefer using get_batch_characteristics for better performance.
    """
    query = """
        SELECT c.name, c.description, scl.effect_direction, scl.evidence_strength
        FROM SNP_Characteristic_Link scl
        JOIN SkinCharacteristic c ON scl.characteristic_id = c.characteristic_id
        WHERE scl.snp_id = :snp_id
    """
    results = conn.execute(sqlalchemy.text(query), {'snp_id': snp_id}).fetchall()
    
    related_skin_characteristics_list = [
            {
                'name': row[0],
                'description': row[1],
                'effect_direction': row[2],
                'evidence_strength': row[3]
            }
            for row in results
        ] if results else []
    
    if not related_skin_characteristics_list:
        logger.info(f"No related skin characteristics found for SNP ID {snp_id}.")
    
    return related_skin_characteristics_list


def get_batch_characteristics(conn, snp_ids):
    """
    Fetches related skin characteristics for multiple SNP IDs in a single query.
    
    Args:
        conn: Database connection
        snp_ids: List of SNP IDs to retrieve characteristics for
        
    Returns:
        Dictionary mapping SNP IDs to lists of characteristic dictionaries
    """
    if not snp_ids:
        return {}
    
    logger.info(f"Batch fetching characteristics for {len(snp_ids)} SNPs")
    
    query = """
        SELECT scl.snp_id, c.name, c.description, scl.effect_direction, scl.evidence_strength
        FROM SNP_Characteristic_Link scl
        JOIN SkinCharacteristic c ON scl.characteristic_id = c.characteristic_id
        WHERE scl.snp_id = ANY(:snp_ids)
    """
    
    results = conn.execute(sqlalchemy.text(query), {'snp_ids': snp_ids}).fetchall()
    logging.info(f"Fetched {len(results)} characteristics records")
    
    # Group characteristics by SNP ID - using numeric indices for tuple access
    characteristics_by_snp = {}
    for row in results:
        # Index positions: 0=snp_id, 1=name, 2=description, 3=effect_direction, 4=evidence_strength
        snp_id = row[0]
        
        if snp_id not in characteristics_by_snp:
            characteristics_by_snp[snp_id] = []
            
        characteristics_by_snp[snp_id].append({
            'name': row[1],
            'description': row[2],
            'effect_direction': row[3],
            'evidence_strength': row[4]
        })
    
    # Log results summary
    found_snps = len(characteristics_by_snp)
    total_chars = sum(len(chars) for chars in characteristics_by_snp.values())
    logger.info(f"Found characteristics for {found_snps} SNPs, total of {total_chars} characteristics")
    
    return characteristics_by_snp

def get_ingredient_recommendations(conn, snp_id):
    """
    Retrieves beneficial and cautionary ingredients linked to this SNP.
    Legacy method - prefer using get_batch_ingredients for better performance.
    """
    beneficial_query = """
        SELECT ingredient_name, ingredient_mechanism, benefit_mechanism, recommendation_strength, evidence_level
        FROM snp_beneficial_ingredients
        WHERE rsid = (SELECT rsid FROM snp WHERE snp_id = :snp_id)
    """
    caution_query = """
        SELECT ic.ingredient_name, ic.risk_mechanism, ic.alternative_ingredients
        FROM SNP_IngredientCaution_Link sicl
        JOIN IngredientCaution ic ON sicl.caution_id = ic.caution_id
        WHERE snp_id = :snp_id
    """
    beneficials = conn.execute(sqlalchemy.text(beneficial_query), {'snp_id': snp_id}).fetchall()
    cautions = conn.execute(sqlalchemy.text(caution_query), {'snp_id': snp_id}).fetchall()

    beneficial_list = [
        {
            'ingredient_name': row[0],
            'ingredient_mechanism': row[1],
            'benefit_mechanism': row[2],
            'recommendation_strength': row[3],
            'evidence_level': row[4]
        }
        for row in beneficials
    ] if beneficials else []
    if not beneficial_list:
        logger.info(f"No beneficial ingredients found for SNP ID {snp_id}.")
    else:
        logger.info(f"Found {len(beneficial_list)} beneficial ingredients for SNP ID {snp_id}.")

    caution_list = [
        {
            'ingredient_name': row[0],
            'risk_mechanism': row[1],
            'alternative_ingredients': row[2]
        }
        for row in cautions
    ] if cautions else []
    if not caution_list:
        logger.info(f"No cautionary ingredients found for SNP ID {snp_id}.")
    else:
        logger.info(f"Found {len(caution_list)} cautionary ingredients for SNP ID {snp_id}.")

    return beneficial_list, caution_list


def get_batch_ingredients(conn, snp_ids):
    """
    Retrieves beneficial and cautionary ingredients for multiple SNP IDs in a single query.
    
    Args:
        conn: Database connection
        snp_ids: List of SNP IDs to retrieve ingredients for
        
    Returns:
        Dictionary mapping SNP IDs to tuples of (beneficial_list, caution_list)
    """
    if not snp_ids:
        return {}
    
    logger.info(f"Batch fetching ingredients for {len(snp_ids)} SNPs")
    
    # Get rsids for the given snp_ids (needed for beneficial ingredients)
    rsid_query = """
        SELECT snp_id, rsid
        FROM snp
        WHERE snp_id = ANY(:snp_ids)
    """
    rsid_results = conn.execute(sqlalchemy.text(rsid_query), {'snp_ids': snp_ids}).fetchall()
    logging.info(f"Fetched {len(rsid_results)} rsid mappings")
    
    # Create mapping of snp_id to rsid - using tuple indices
    snp_to_rsid = {row[0]: row[1] for row in rsid_results}
    
    # Get all beneficial ingredients in one query
    beneficial_query = """
        SELECT s.snp_id, bi.ingredient_name, bi.ingredient_mechanism, 
               bi.benefit_mechanism, bi.recommendation_strength, bi.evidence_level
        FROM snp s
        JOIN snp_beneficial_ingredients bi ON s.rsid = bi.rsid
        WHERE s.snp_id = ANY(:snp_ids)
    """
    
    # Get all cautionary ingredients in one query
    caution_query = """
        SELECT sicl.snp_id, ic.ingredient_name, ic.risk_mechanism, ic.alternative_ingredients
        FROM SNP_IngredientCaution_Link sicl
        JOIN IngredientCaution ic ON sicl.caution_id = ic.caution_id
        WHERE sicl.snp_id = ANY(:snp_ids)
    """
    
    beneficial_results = conn.execute(sqlalchemy.text(beneficial_query), {'snp_ids': snp_ids}).fetchall()
    caution_results = conn.execute(sqlalchemy.text(caution_query), {'snp_ids': snp_ids}).fetchall()
    
    logging.info(f"Fetched {len(beneficial_results)} beneficial ingredients and {len(caution_results)} cautions")
    
    # Initialize results dictionary
    ingredients_by_snp = {snp_id: ([], []) for snp_id in snp_ids}
    
    # Process beneficial ingredients - using tuple indices
    for row in beneficial_results:
        # Index positions: 0=snp_id, 1=ingredient_name, 2=ingredient_mechanism, 
        #                 3=benefit_mechanism, 4=recommendation_strength, 5=evidence_level
        snp_id = row[0]
        beneficial_list, _ = ingredients_by_snp[snp_id]
        
        beneficial_list.append({
            'ingredient_name': row[1],
            'ingredient_mechanism': row[2],
            'benefit_mechanism': row[3],
            'recommendation_strength': row[4],
            'evidence_level': row[5]
        })
    
    # Process cautionary ingredients - using tuple indices
    for row in caution_results:
        # Index positions: 0=snp_id, 1=ingredient_name, 2=risk_mechanism, 3=alternative_ingredients
        snp_id = row[0]
        _, caution_list = ingredients_by_snp[snp_id]
        
        caution_list.append({
            'ingredient_name': row[1],
            'risk_mechanism': row[2],
            'alternative_ingredients': row[3]
        })
    
    # Log results
    total_beneficial = sum(len(b) for b, _ in ingredients_by_snp.values())
    total_cautions = sum(len(c) for _, c in ingredients_by_snp.values())
    logger.info(f"Found {total_beneficial} beneficial ingredients and {total_cautions} cautions across {len(snp_ids)} SNPs")
    
    return ingredients_by_snp

def get_complete_snp_data(conn, rsids):
    """
    Retrieves complete SNP data including characteristics and ingredients in a single query.
    
    Args:
        conn: Database connection
        rsids: List of rsid values to retrieve
        
    Returns:
        List of dictionaries with complete SNP data
    """
    if not rsids:
        return []
        
    logger.info(f"Fetching complete data for {len(rsids)} SNPs")
    
    # Using a combination of JSON aggregation and subqueries for optimal performance
    query = """
    WITH relevant_snps AS (
        SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category
        FROM snp
        WHERE rsid = ANY(:rsids)
    )
    SELECT 
        s.snp_id, 
        s.rsid, 
        s.gene, 
        s.risk_allele, 
        s.effect, 
        s.evidence_strength, 
        s.category,
        -- Characteristics as JSON array
        COALESCE(
            (SELECT json_agg(json_build_object(
                'name', c.name,
                'description', c.description,
                'effect_direction', scl.effect_direction,
                'evidence_strength', scl.evidence_strength
            ))
            FROM snp_characteristic_link scl
            JOIN skincharacteristic c ON scl.characteristic_id = c.characteristic_id
            WHERE scl.snp_id = s.snp_id),
            '[]'::json
        ) as characteristics,
        -- Beneficial ingredients as JSON array
        COALESCE(
            (SELECT json_agg(json_build_object(
                'ingredient_name', bi.ingredient_name,
                'ingredient_mechanism', bi.ingredient_mechanism,
                'benefit_mechanism', bi.benefit_mechanism,
                'recommendation_strength', bi.recommendation_strength,
                'evidence_level', bi.evidence_level
            ))
            FROM snp_beneficial_ingredients bi
            WHERE bi.rsid = s.rsid),
            '[]'::json
        ) as beneficial_ingredients,
        -- Cautionary ingredients as JSON array
        COALESCE(
            (SELECT json_agg(json_build_object(
                'ingredient_name', ic.ingredient_name,
                'risk_mechanism', ic.risk_mechanism,
                'alternative_ingredients', ic.alternative_ingredients
            ))
            FROM snp_ingredientcaution_link sicl
            JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
            WHERE sicl.snp_id = s.snp_id),
            '[]'::json
        ) as caution_ingredients
    FROM relevant_snps s
    """
    
    results = conn.execute(sqlalchemy.text(query), {'rsids': rsids}).fetchall()
    logging.info(f"Fetched complete data for {len(results)} SNPs")
    
    # Process results - using indices for tuple results
    complete_data = []
    for row in results:
        # Index positions: 0=snp_id, 1=rsid, 2=gene, 3=risk_allele, 4=effect, 5=evidence_strength,
        #                  6=category, 7=characteristics, 8=beneficial_ingredients, 9=caution_ingredients
        snp_data = {
            'snp_id': row[0],
            'rsid': row[1],
            'gene': row[2],
            'risk_allele': row[3],
            'effect': row[4],
            'evidence_strength': row[5],
            'category': row[6],
            'characteristics': row[7],
            'beneficial_ingredients': row[8],
            'caution_ingredients': row[9]
        }
        complete_data.append(snp_data)
    
    logger.info(f"Processed complete data for {len(complete_data)} SNPs")
    return complete_data


def get_dynamic_summary(conn, report_data):
    """
    Gets dynamically generated summary using the SQL summary function
    """
    variants = [m['rsid'] for m in report_data['mutations']]
    variants_str = '{' + ','.join(f'"{v}"' for v in variants) + '}'
   
    query = """
    WITH genetic_results AS (
        SELECT * FROM generate_genetic_analysis_section(CAST(:variants_str AS text[]))
    )
    SELECT generate_summary_section(
        CAST(:variants_str AS text[]),
        (SELECT findings FROM genetic_results)
    );
    """
    try:
        # Create the SQLAlchemy text object
        sql_text = sqlalchemy.text(query)
        
        # Bind the parameters
        compiled = sql_text.bindparams(variants_str=variants_str).compile(
            compile_kwargs={"literal_binds": True}
        )
        
        # Log the fully rendered SQL command
        logger.debug(f"Executing query: {str(compiled)}")

        # Execute the query
        summary = conn.execute(compiled).fetchone()[0]
    except Exception as e:
        logger.info(f"Error generating summary: {e}")
        raise e
    return summary

def assemble_report_data(conn, parsed_snps):
    """
    Puts together the final report structure, but ONLY includes SNPs
    if the user's genotype contains the known 'risk_allele'.
    
    Optimized version using batch processing for better performance.
    """
    logger.info(f"Assembling report data for {len(parsed_snps)} SNPs")
    start_time = time.time()
    
    # Extract rsids from parsed SNPs
    rsids = [snp['rsid'] for snp in parsed_snps]
    
    # Use the optimized batch query to get SNP details
    logger.info("Fetching SNP details in batch")
    snp_details = get_batch_snp_details(conn, rsids)
    
    # Initialize report structure
    report = {
        'mutations': [],
        'ingredient_recommendations': {
            'prioritize': [],
            'caution': []
        }
    }
    
    # Filter SNPs that match user's risk allele
    matching_snps = []
    matching_snp_ids = []
    
    for snp in parsed_snps:
        # Skip if not in our database
        if snp['rsid'] not in snp_details:
            continue
            
        snp_detail = snp_details[snp['rsid']]
        user_alleles = [snp['allele1'].upper(), snp['allele2'].upper()]
        risk_allele = snp_detail['risk_allele'].upper()
        
        # Skip if risk allele not present
        if risk_allele not in user_alleles:
            continue
            
        # Store matching SNPs and their IDs
        matching_snps.append({
            'parsed_snp': snp,
            'snp_detail': snp_detail
        })
        matching_snp_ids.append(snp_detail['snp_id'])
    
    logger.info(f"Found {len(matching_snps)} SNPs with matching risk alleles")
    
    if not matching_snps:
        logger.info("No matching SNPs found")
        return report
    
    # Batch fetch characteristics and ingredients
    characteristics_by_snp = get_batch_characteristics(conn, matching_snp_ids)
    ingredients_by_snp = get_batch_ingredients(conn, matching_snp_ids)
    
    # Assemble the report
    for match in matching_snps:
        snp = match['parsed_snp']
        snp_detail = match['snp_detail']
        snp_id = snp_detail['snp_id']
        
        # Get characteristics
        characteristics = characteristics_by_snp.get(snp_id, [])
        
        # Create mutation entry
        mutation = {
            'gene': snp_detail['gene'],
            'rsid': snp['rsid'],
            'allele1': snp['allele1'],
            'allele2': snp['allele2'],
            'risk_allele': snp_detail['risk_allele'],
            'effect': snp_detail['effect'],
            'evidence_strength': snp_detail['evidence_strength'],
            'category': snp_detail['category'],
            'characteristics': characteristics
        }
        report['mutations'].append(mutation)
        
        # Add ingredients if available
        if snp_id in ingredients_by_snp:
            beneficials, cautions = ingredients_by_snp[snp_id]
            report['ingredient_recommendations']['prioritize'].extend(beneficials)
            report['ingredient_recommendations']['caution'].extend(cautions)
    
    # Calculate and log performance metrics
    elapsed_time = time.time() - start_time
    logger.info(f"Report assembly completed in {elapsed_time:.2f} seconds")
    logger.info(f"Report contains {len(report['mutations'])} mutations")
    logger.info(f"Report contains {len(report['ingredient_recommendations']['prioritize'])} beneficial ingredients")
    logger.info(f"Report contains {len(report['ingredient_recommendations']['caution'])} cautionary ingredients")
    
    return report

def markdown_to_pdf(markdown_content, output_path):
    """
    Convert markdown content to a PDF file using ReportLab.
    
    Args:
        markdown_content (str): Markdown formatted text
        output_path (str): Path to save the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72, 
        leftMargin=72,
        topMargin=72, 
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Create custom styles with unique names
    custom_heading1 = ParagraphStyle(
        name='CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12
    )
    
    custom_heading2 = ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=10,
        spaceBefore=12
    )
    
    custom_heading3 = ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=10
    )
    
    custom_body = ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14
    )
    
    custom_list_item = ParagraphStyle(
        name='CustomListItem',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        leftIndent=20
    )
    
    # Add the custom styles to the stylesheet
    styles.add(custom_heading1)
    styles.add(custom_heading2)
    styles.add(custom_heading3)
    styles.add(custom_body)
    styles.add(custom_list_item)
    
    # Split markdown into sections
    sections = markdown_content.split('\n## ')
    
    # Prepare elements for the PDF
    elements = []
    
    # Process the title section
    title_section = sections[0].strip()
    title_lines = title_section.split('\n')
    
    # Main title
    title = title_lines[0].replace('# ', '')
    elements.append(Paragraph(title, styles['CustomHeading1']))
    elements.append(Spacer(1, 12))
    
    # Subtitle if present
    if len(title_lines) > 1:
        subtitle = title_lines[1].replace('## ', '')
        elements.append(Paragraph(subtitle, styles['CustomHeading3']))
        elements.append(Spacer(1, 12))
    
    # Process other sections
    for i, section in enumerate(sections[1:], 1):
        section_lines = section.split('\n')
        section_title = section_lines[0]
        section_content = '\n'.join(section_lines[1:])
        
        # Add section header
        elements.append(Paragraph(section_title, styles['CustomHeading2']))
        elements.append(Spacer(1, 6))
        
        # Process content based on section type
        if "Your Genetic Mutations" in section_title:
            # Process table
            table_lines = [line.strip() for line in section_content.split('\n') if '|' in line and line.strip()]
            if len(table_lines) >= 2:  # Header and separator line
                header = table_lines[0]
                data_rows = table_lines[2:]  # Skip separator line
                
                # Parse header
                headers = [cell.strip() for cell in header.split('|')[1:-1]]
                
                # Create table data
                table_data = [headers]
                for row in data_rows:
                    cells = [cell.strip() for cell in row.split('|')[1:-1]]
                    table_data.append(cells)
                
                # Create table
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 12))
            
        else:
            # Process regular paragraphs and lists
            paragraphs = section_content.split('\n\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Check if it's a header section
                    if paragraph.startswith('### '):
                        header_text = paragraph.replace('### ', '')
                        elements.append(Paragraph(header_text, styles['CustomHeading3']))
                    # Check if it's a list
                    elif paragraph.startswith('- '):
                        list_items = paragraph.split('\n- ')
                        for item in list_items:
                            if item.strip():
                                # Replace markdown bold with HTML bold
                                item = item.replace('**', '<b>', 1).replace('**', '</b>', 1)
                                elements.append(Paragraph(f"• {item.strip()}", styles['CustomListItem']))
                                elements.append(Spacer(1, 4))
                    else:
                        # Regular paragraph
                        elements.append(Paragraph(paragraph, styles['CustomBody']))
                        elements.append(Spacer(1, 8))
    
    # Build the PDF
    doc.build(elements)
    return output_path

def generate_markdown(report_data, output_path, conn):
    """
    Creates a markdown-formatted report and converts it to PDF.
    """
    try:
        summary_text = get_dynamic_summary(conn, report_data)
    except Exception as e:
        logger.warning(f"Error getting dynamic summary: {e}")
        summary_text = "Your genes reveal how your skin naturally behaves. This report guides you on how to optimize your skincare based on your genetics."
    
    # Build the markdown content
    markdown_content = f"""# Your Genetic Skincare Report
## A story written by your DNA

## Summary: The Story of Your Skin
{summary_text}

## Your Genetic Mutations

| Gene | rsID | Alleles | Impact |
|------|------|---------|--------|
"""
    
    # Add mutation rows
    for mutation in report_data['mutations']:
        alleles = f"{mutation['allele1']}/{mutation['allele2']}"
        markdown_content += f"| {mutation['gene']} | {mutation['rsid']} | {alleles} | {mutation['effect']} |\n"
    
    # Add characteristics section if available
    any_characteristics = False
    for mutation in report_data['mutations']:
        if mutation.get('characteristics') and len(mutation['characteristics']) > 0:
            any_characteristics = True
            break
    
    if any_characteristics:
        markdown_content += "\n## Skin Characteristics Affected\n\n"
        markdown_content += "\n"
        for mutation in report_data['mutations']:
            if mutation.get('characteristics') and len(mutation['characteristics']) > 0:
                markdown_content += f"### {mutation['gene']} ({mutation['category']})\n\n"
                for char in mutation['characteristics']:
                    effect = char.get('effect_direction', 'Affects')
                    markdown_content += f"- **{char['name']}**: {effect} - {char['description']}\n"
                markdown_content += "\n"
    
    # Add ingredient recommendations
    markdown_content += "\n## Ingredient Recommendations\n\n"
    
    # Prioritized ingredients
    markdown_content += "\n### Prioritize These\n\n"
    
    seen_ingredients = set()
    unique_prioritize = []
    for ingr in report_data['ingredient_recommendations']['prioritize']:
        if ingr['ingredient_name'] not in seen_ingredients:
            seen_ingredients.add(ingr['ingredient_name'])
            unique_prioritize.append(ingr)
    
    for ingr in unique_prioritize:
        markdown_content += f"- **{ingr['ingredient_name']}**: {ingr['benefit_mechanism']}\n"
    
    # Cautionary ingredients
    markdown_content += "\n### Approach With Caution\n\n"
    
    seen_cautions = set()
    unique_cautions = []
    for ingr in report_data['ingredient_recommendations']['caution']:
        if ingr['ingredient_name'] not in seen_cautions:
            seen_cautions.add(ingr['ingredient_name'])
            unique_cautions.append(ingr)
    
    for ingr in unique_cautions:
        markdown_content += f"- **{ingr['ingredient_name']}**: {ingr['risk_mechanism']}\n"
    
    # Save markdown content to temp file if needed for debugging
    md_path = output_path.replace('.pdf', '.md')
    with open(md_path, 'w') as f:
        f.write(markdown_content)
    
    # Convert markdown to PDF
    return markdown_to_pdf(markdown_content, output_path)

def generate_pdf(report_data, output_path, conn):
    """
    Creates a PDF summarizing the relevant SNPs and recommended ingredients.
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Your Genetic Skincare Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, "A story written by your DNA")

    summary_text = get_dynamic_summary(conn, report_data)
   
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 110, "Summary: The Story of Your Skin")
    c.setFont("Helvetica", 10)
   
    txt_obj = c.beginText(50, height - 130)
    for line in summary_text.split('\n'):
        txt_obj.textLine(line.strip())
    c.drawText(txt_obj)

    y = height - 400
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Your Genetic Mutations")
    y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Gene")
    c.drawString(120, y, "rsID")
    c.drawString(190, y, "Alleles")
    c.drawString(250, y, "Impact")
    y -= 15
    c.setFont("Helvetica", 10)

    for mutation in report_data['mutations']:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
           
        line = f"{mutation['gene']}   {mutation['rsid']}   {mutation['allele1']}/{mutation['allele2']}   {mutation['effect']}"
        c.drawString(50, y, line)
        y -= 15

    y -= 20
    if y < 100:
        c.showPage()
        y = height - 50
       
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Ingredient Recommendations")
    y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Prioritize These:")
    y -= 15
    c.setFont("Helvetica", 10)
   
    seen_ingredients = set()
    unique_prioritize = []
    for ingr in report_data['ingredient_recommendations']['prioritize']:
        if ingr['ingredient_name'] not in seen_ingredients:
            seen_ingredients.add(ingr['ingredient_name'])
            unique_prioritize.append(ingr)

    for ingr in unique_prioritize:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
           
        line = f"{ingr['ingredient_name']}: {ingr['benefit_mechanism']}"
        c.drawString(60, y, line)
        y -= 12

    y -= 15
    if y < 100:
        c.showPage()
        y = height - 50
       
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Approach With Caution:")
    y -= 15
    c.setFont("Helvetica", 10)

    seen_cautions = set()
    unique_cautions = []
    for ingr in report_data['ingredient_recommendations']['caution']:
        if ingr['ingredient_name'] not in seen_cautions:
            seen_cautions.add(ingr['ingredient_name'])
            unique_cautions.append(ingr)

    for ingr in unique_cautions:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
           
        line = f"{ingr['ingredient_name']}: {ingr['risk_mechanism']}"
        c.drawString(60, y, line)
        y -= 12

    c.save()

def log_report_generation(conn, report_data):
    """
    If you have a 'report_log' table, this logs the entire final JSON data.
    """
    query = "INSERT INTO report_log (generated_at, report_summary) VALUES (NOW(), :report_summary)"
    data_json = json.dumps(report_data)
    conn.execute(sqlalchemy.text(query), {'report_summary': data_json})


def main():
    if len(sys.argv) != 3:
        logger.info(
            "Usage: python process_dna.py <input_dna_file.txt> <output_report.pdf>")
        sys.exit(1)

    dna_file = sys.argv[1]
    output_pdf = sys.argv[2]

    parsed_snps = read_dna_file(dna_file)
    logger.info(f"Parsed {len(parsed_snps)} SNP records from {dna_file}.")

    engine = connect_to_database()
    logger.info("Database connection established.")

    with engine.connect() as conn:
        report_data = assemble_report_data(conn, parsed_snps)
        logger.info("Report data assembled.")

        generate_pdf(report_data, output_pdf, conn)
        logger.info(f"PDF report created: {output_pdf}")

        # try:
        #     log_report_generation(conn, report_data)
        #     logger.info("Report generation logged.")
        # except Exception as e:
        #     logger.info(f"Error logging report generation: {e}")



if __name__ == "__main__":
    main()