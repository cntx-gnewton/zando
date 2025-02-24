#!/usr/bin/env python3
import sys
import json
import os
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd
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

logger.info(f"{os.environ['INSTANCE_CONNECTION_NAME']}, {os.environ['DB_USER']}, {os.environ['DB_PASS']}, {os.environ['DB_NAME']}")

 
def read_dna_file(file_path):
    """
    Reads an AncestryDNA raw data .txt file and extracts SNP records.
    Skips header lines (#) and the column header.
    Returns a list of dicts with keys: rsid, chromosome, position, allele1, allele2.
    """
    snps = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue
            # Skip the header row if present
            if line.startswith("rsid"):
                continue

            fields = line.split("\t")
            if len(fields) >= 5:
                rsid, chromosome, position, allele1, allele2 = fields[:5]
                snps.append({
                    'rsid': rsid,
                    'chromosome': chromosome,
                    'position': position,
                    'allele1': allele1,
                    'allele2': allele2
                })
    return snps

def connect_to_database() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
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

    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    return pool


def load_snp_table(conn):
    """
    Loads the SNP table into a pandas DataFrame.
    """
    query = "SELECT * FROM snp"
    df = pd.read_sql(query, conn)
    logger.debug(f"Loaded {len(df)} SNP records from the database.")
    return df


def get_snp_details(df, rsid):
    """
    Retrieves SNP details from the pandas DataFrame using the provided rsid.
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

def get_ingredient_recommendations(conn, snp_id):
    """
    Retrieves beneficial and cautionary ingredients linked to this SNP.
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
    """
    snp_df = load_snp_table(conn)

    report = {
        'mutations': [],
        'ingredient_recommendations': {
            'prioritize': [],
            'caution': []
        }
    }

    for snp in parsed_snps:
        snp_detail = get_snp_details(snp_df, snp['rsid'])
        if not snp_detail:
            continue  # Not in our SNP table, skip

        user_alleles = [snp['allele1'].upper(), snp['allele2'].upper()]
        risk_allele = snp_detail['risk_allele'].upper()

        if risk_allele not in user_alleles:
            continue

        mutation = {
            'gene': snp_detail['gene'],
            'rsid': snp['rsid'],
            'allele1': snp['allele1'],
            'allele2': snp['allele2'],
            'risk_allele': snp_detail['risk_allele'],
            'effect': snp_detail['effect'],
            'evidence_strength': snp_detail['evidence_strength'],
            'category': snp_detail['category'],
            'characteristics': get_related_skin_characteristics(conn, snp_detail['snp_id'])
        }
        report['mutations'].append(mutation)

        beneficials, cautions = get_ingredient_recommendations(
            conn, snp_detail['snp_id'])
        report['ingredient_recommendations']['prioritize'].extend(beneficials)
        report['ingredient_recommendations']['caution'].extend(cautions)

    return report

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