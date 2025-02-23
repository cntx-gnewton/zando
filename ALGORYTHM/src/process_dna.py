#!/usr/bin/env python3
import sys
import json
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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


def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of Postgres.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

    ip_type = IPTypes.PRIVATE if os.environ.get(
        "PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
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

    # The Cloud SQL Python Connector can be used with SQLAlchemy
    # using the 'creator' argument to 'create_engine'
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
        # ...
    )
    return pool




def connect_to_database():
   """
   Adjust these parameters to match your actual DB config.
   """
   conn = psycopg2.connect(
       host="localhost",
       database="algorythm",     
       user="cam",              
       password="Astrohippy150!"
   )
   return conn

def get_snp_details(conn, rsid):
   """
   Retrieves SNP details from the 'snp' table using the provided rsid.
   """
   query = """
       SELECT snp_id, gene, risk_allele, effect, evidence_strength, category 
       FROM snp
       WHERE rsid = %s
   """
   with conn.cursor() as cur:
       cur.execute(query, (rsid,))
       row = cur.fetchone()
       if row:
           return {
               'snp_id': row[0],
               'gene': row[1],
               'risk_allele': row[2],
               'effect': row[3],
               'evidence_strength': row[4],
               'category': row[5]
           }
       return None

def get_related_skin_characteristics(conn, snp_id):
   """
   Fetches any related skin characteristics via SNP_Characteristic_Link.
   """
   query = """
       SELECT c.name, c.description, scl.effect_direction, scl.evidence_strength
       FROM SNP_Characteristic_Link scl
       JOIN SkinCharacteristic c ON scl.characteristic_id = c.characteristic_id
       WHERE scl.snp_id = %s
   """
   with conn.cursor() as cur:
       cur.execute(query, (snp_id,))
       rows = cur.fetchall()
       return [
           {
               'name': r[0],
               'description': r[1],
               'effect_direction': r[2],
               'evidence_strength': r[3]
           }
           for r in rows
       ]

def get_ingredient_recommendations(conn, snp_id):
   """
   Retrieves beneficial and cautionary ingredients linked to this SNP.
   """
   beneficial_query = """
       SELECT ingredient_name, ingredient_mechanism, benefit_mechanism, recommendation_strength, evidence_level
       FROM snp_beneficial_ingredients
       WHERE rsid = (SELECT rsid FROM snp WHERE snp_id = %s)
   """
   caution_query = """
       SELECT ic.ingredient_name, ic.risk_mechanism, ic.alternative_ingredients
       FROM SNP_IngredientCaution_Link sicl
       JOIN IngredientCaution ic ON sicl.caution_id = ic.caution_id
       WHERE snp_id = %s
   """
   with conn.cursor() as cur:
       cur.execute(beneficial_query, (snp_id,))
       beneficials = cur.fetchall()

       cur.execute(caution_query, (snp_id,))
       cautions = cur.fetchall()

   beneficial_list = []
   for b in beneficials:
       beneficial_list.append({
           'ingredient_name': b[0],
           'ingredient_mechanism': b[1],
           'benefit_mechanism': b[2],
           'recommendation_strength': b[3],
           'evidence_level': b[4],
       })

   caution_list = []
   for ctn in cautions:
       caution_list.append({
           'ingredient_name': ctn[0],
           'risk_mechanism': ctn[1],
           'alternative_ingredients': ctn[2],
       })

   return beneficial_list, caution_list

def get_dynamic_summary(conn, report_data):
   """
   Gets dynamically generated summary using the SQL summary function
   """
   # Convert mutations to array of rsids for the SQL function
   variants = [m['rsid'] for m in report_data['mutations']]
   variants_str = '{' + ','.join(f'"{v}"' for v in variants) + '}'
   
   query = """
   WITH genetic_results AS (
       SELECT * FROM generate_genetic_analysis_section(%s::text[])
   )
   SELECT generate_summary_section(
       %s::text[],
       (SELECT findings FROM genetic_results)
   );
   """
   
   with conn.cursor() as cur:
       cur.execute(query, (variants_str, variants_str))
       summary = cur.fetchone()[0]
       return summary

def assemble_report_data(conn, parsed_snps):
   """
   Puts together the final report structure, but ONLY includes SNPs
   if the user's genotype contains the known 'risk_allele'.
   """
   report = {
       'mutations': [],
       'ingredient_recommendations': {
           'prioritize': [],
           'caution': []
       }
   }

   for snp in parsed_snps:
       snp_detail = get_snp_details(conn, snp['rsid'])
       if not snp_detail:
           continue  # Not in our SNP table, skip
       
       # Check genotype: do the user's alleles contain the risk allele?
       user_alleles = [snp['allele1'].upper(), snp['allele2'].upper()]
       risk_allele = snp_detail['risk_allele'].upper()

       if risk_allele not in user_alleles:
           # The user does NOT carry the risk allele, so skip
           continue

       # If we get here, the user indeed has at least one risk allele
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

       # Now get any relevant ingredient recs or cautions
       beneficials, cautions = get_ingredient_recommendations(conn, snp_detail['snp_id'])
       report['ingredient_recommendations']['prioritize'].extend(beneficials)
       report['ingredient_recommendations']['caution'].extend(cautions)

   return report

def generate_pdf(report_data, output_path, conn):
   """
   Creates a PDF summarizing the relevant SNPs and recommended ingredients.
   """
   c = canvas.Canvas(output_path, pagesize=letter)
   width, height = letter

   # Title
   c.setFont("Helvetica-Bold", 20)
   c.drawString(50, height - 50, "Your Genetic Skincare Report")
   c.setFont("Helvetica", 12)
   c.drawString(50, height - 75, "A story written by your DNA")

   # Get dynamic summary
   summary_text = get_dynamic_summary(conn, report_data)
   
   # Summary
   c.setFont("Helvetica-Bold", 14)
   c.drawString(50, height - 110, "Summary: The Story of Your Skin")
   c.setFont("Helvetica", 10)
   
   # Handle the multi-line summary text
   txt_obj = c.beginText(50, height - 130)
   for line in summary_text.split('\n'):
       txt_obj.textLine(line.strip())
   c.drawText(txt_obj)

   # Genetic Mutations
   y = height - 400  # Adjusted for potentially longer summary
   c.setFont("Helvetica-Bold", 12)
   c.drawString(50, y, "Your Genetic Mutations")
   y -= 20

   # Table header
   c.setFont("Helvetica-Bold", 10)
   c.drawString(50, y, "Gene")
   c.drawString(120, y, "rsID")
   c.drawString(190, y, "Alleles")
   c.drawString(250, y, "Impact")
   y -= 15
   c.setFont("Helvetica", 10)

   # Loop SNPs
   for mutation in report_data['mutations']:
       if y < 50:  # Start new page if we're near the bottom
           c.showPage()
           y = height - 50
           c.setFont("Helvetica", 10)
           
       line = f"{mutation['gene']}   {mutation['rsid']}   {mutation['allele1']}/{mutation['allele2']}   {mutation['effect']}"
       c.drawString(50, y, line)
       y -= 15

   # Ingredient Recommendations
   y -= 20
   if y < 100:  # Start new page if less than 100 points from bottom
       c.showPage()
       y = height - 50
       
   c.setFont("Helvetica-Bold", 12)
   c.drawString(50, y, "Ingredient Recommendations")
   y -= 20

   # Prioritize
   c.setFont("Helvetica-Bold", 10)
   c.drawString(50, y, "Prioritize These:")
   y -= 15
   c.setFont("Helvetica", 10)
   
   # Remove duplicates from prioritize list
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

   # Caution
   y -= 15
   if y < 100:
       c.showPage()
       y = height - 50
       
   c.setFont("Helvetica-Bold", 10)
   c.drawString(50, y, "Approach With Caution:")
   y -= 15
   c.setFont("Helvetica", 10)

   # Remove duplicates from caution list
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
   query = "INSERT INTO report_log (generated_at, report_summary) VALUES (NOW(), %s)"
   data_json = json.dumps(report_data)
   with conn.cursor() as cur:
       cur.execute(query, (data_json,))
       conn.commit()

def main():
   if len(sys.argv) != 3:
       print("Usage: python process_dna.py <input_dna_file.txt> <output_report.pdf>")
       sys.exit(1)

   dna_file = sys.argv[1]
   output_pdf = sys.argv[2]

   parsed_snps = read_dna_file(dna_file)
   print(f"Parsed {len(parsed_snps)} SNP records from {dna_file}.")

   try:
       conn = connect_to_database()
       print("Database connection established.")
       
       report_data = assemble_report_data(conn, parsed_snps)
       print("Report data assembled.")

       generate_pdf(report_data, output_pdf, conn)
       print(f"PDF report created: {output_pdf}")

       try:
           log_report_generation(conn, report_data)
           print("Report generation logged.")
       except Exception as e:
           print(f"Error logging report generation: {e}")

       conn.close()
   except Exception as e:
       print(f"Database Error: {e}")
       sys.exit(1)

if __name__ == "__main__":
   main()
