#!/usr/bin/env python3
import sys
import json
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# -------------------------------
# Section 1: Reading & Parsing the DNA File
# -------------------------------
def read_dna_file(file_path):
    """
    Reads an AncestryDNA raw data .txt file and extracts SNP records.
    Skips header lines (lines starting with "#") and the column header.
    Returns a list of dictionaries with keys: rsid, chromosome, position, allele1, allele2.
    """
    snps = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip comments (#) and empty lines
            if line.startswith("#") or not line:
                continue
            # Skip the header row if present (e.g. "rsid    chromosome    position    allele1    allele2")
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

# -------------------------------
# Section 2: Connecting to the SQL Database
# -------------------------------
def connect_to_database():
    """
    Establishes a connection to the PostgreSQL database.
    Returns the connection object.

    IMPORTANT: Update the parameters below (database, user, password)
    to match your actual database configuration.
    """
    conn = psycopg2.connect(
        host="localhost",
        database="algorythm",      # Use your actual DB name, e.g. 'algorythm'
        user="cam",                # Use the DB user you actually connect with, e.g. 'cam'
        password="Astrohippy150!"  # Update with your actual password, if any
    )
    return conn

# -------------------------------
# Section 3: Fetching SNP Details from the Database
# -------------------------------
def get_snp_details(conn, rsid):
    """
    Retrieves SNP details from the database using the provided rsid.
    Returns a dictionary with SNP details if found, or None if not.
    """
    query = """
        SELECT snp_id, gene, risk_allele, effect, evidence_strength, category 
        FROM snp 
        WHERE rsid = %s
    """
    with conn.cursor() as cur:
        cur.execute(query, (rsid,))
        result = cur.fetchone()
        if result:
            return {
                'snp_id': result[0],
                'gene': result[1],
                'risk_allele': result[2],
                'effect': result[3],
                'evidence_strength': result[4],
                'category': result[5]
            }
        return None

# -------------------------------
# Section 4: Fetching Related Skin Characteristics
# -------------------------------
def get_related_skin_characteristics(conn, snp_id):
    """
    Retrieves skin characteristics associated with the given snp_id
    from the SNP_Characteristic_Link table.
    Returns a list of dictionaries.
    """
    query = """
        SELECT c.name, c.description, scl.effect_direction, scl.evidence_strength
        FROM SNP_Characteristic_Link scl
        JOIN SkinCharacteristic c ON scl.characteristic_id = c.characteristic_id
        WHERE scl.snp_id = %s
    """
    with conn.cursor() as cur:
        cur.execute(query, (snp_id,))
        results = cur.fetchall()
        characteristics = []
        for row in results:
            characteristics.append({
                'name': row[0],
                'description': row[1],
                'effect_direction': row[2],
                'evidence_strength': row[3]
            })
    return characteristics

# -------------------------------
# Section 5: Fetching Ingredient Recommendations
# -------------------------------
def get_ingredient_recommendations(conn, snp_id):
    """
    Retrieves beneficial ingredient recommendations and cautionary ingredients
    for the given snp_id using:
      - snp_beneficial_ingredients (view) for beneficials.
      - SNP_IngredientCaution_Link & IngredientCaution for cautions.
    Returns two lists: beneficial_list, caution_list.
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
        # Beneficial ingredients
        cur.execute(beneficial_query, (snp_id,))
        beneficials = cur.fetchall()

        # Cautionary ingredients
        cur.execute(caution_query, (snp_id,))
        cautions = cur.fetchall()

    # Convert to list of dicts
    beneficial_list = [{
        'ingredient_name': row[0],
        'ingredient_mechanism': row[1],
        'benefit_mechanism': row[2],
        'recommendation_strength': row[3],
        'evidence_level': row[4]
    } for row in beneficials]

    caution_list = [{
        'ingredient_name': row[0],
        'risk_mechanism': row[1],
        'alternative_ingredients': row[2]
    } for row in cautions]

    return beneficial_list, caution_list

# -------------------------------
# Section 6: Assembling the Report Data
# -------------------------------
def assemble_report_data(conn, parsed_snps):
    """
    Combines the parsed DNA SNP data with additional details from the database.
    Returns a dictionary with:
      - 'mutations': A list of SNP mutation details
      - 'ingredient_recommendations': { 'prioritize': [...], 'caution': [...] }
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
        if snp_detail:
            # Gather the SNP info
            mutation = {
                'gene': snp_detail['gene'],
                'rsid': snp['rsid'],
                'risk_allele': snp_detail['risk_allele'],
                'effect': snp_detail['effect'],
                'evidence_strength': snp_detail['evidence_strength'],
                'category': snp_detail['category'],
                'characteristics': get_related_skin_characteristics(conn, snp_detail['snp_id'])
            }
            report['mutations'].append(mutation)

            # Fetch ingredient recs
            beneficials, cautions = get_ingredient_recommendations(conn, snp_detail['snp_id'])
            # Add them to the overall lists
            report['ingredient_recommendations']['prioritize'].extend(beneficials)
            report['ingredient_recommendations']['caution'].extend(cautions)

    return report

# -------------------------------
# Section 7: Generating the PDF Report
# -------------------------------
def generate_pdf(report_data, output_path):
    """
    Generates a PDF report from the report_data dictionary using ReportLab.
    The PDF includes:
      - Title and summary
      - A table of genetic mutations
      - Ingredient recommendations (prioritized vs caution)
    """
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title Section
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Your Genetic Skincare Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 75, "A story written by your DNA")

    # Summary Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 110, "Summary: The Story of Your Skin")
    c.setFont("Helvetica", 10)
    summary_text = (
        "Your genes reveal how your skin naturally behaves—like a hidden instruction manual. "
        "Based on your DNA, your skin may struggle to retain moisture, process antioxidants slowly, "
        "and break down collagen faster than average. This report guides you on how to hack your "
        "genetics for healthier skin."
    )
    text_obj = c.beginText(50, height - 130)
    text_obj.textLines(summary_text)
    c.drawText(text_obj)

    # Genetic Mutations Table
    y = height - 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Your Genetic Mutations")
    y -= 20

    # Table Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Gene")
    c.drawString(150, y, "Mutation")
    c.drawString(250, y, "Impact in Plain English")
    y -= 15
    c.setFont("Helvetica", 10)

    # Mutation Rows
    for mutation in report_data['mutations']:
        line = f"{mutation['gene']}   {mutation['rsid']}   {mutation['effect']}"
        c.drawString(50, y, line)
        y -= 15

    # Ingredient Recommendations
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Ingredient Recommendations")
    y -= 20

    # Prioritize Section
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Prioritize These:")
    y -= 15
    c.setFont("Helvetica", 10)
    for ingr in report_data['ingredient_recommendations']['prioritize']:
        line = f"{ingr['ingredient_name']}: {ingr['benefit_mechanism']}"
        c.drawString(60, y, line)
        y -= 12

    # Caution Section
    y -= 15
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Approach With Caution:")
    y -= 15
    c.setFont("Helvetica", 10)
    for ingr in report_data['ingredient_recommendations']['caution']:
        line = f"{ingr['ingredient_name']}: {ingr['risk_mechanism']}"
        c.drawString(60, y, line)
        y -= 12

    c.save()

# -------------------------------
# Section 8: Logging Report Generation (Optional)
# -------------------------------
def log_report_generation(conn, report_data):
    """
    Logs report generation details in the database.
    Assumes the existence of a 'report_log' table with columns (generated_at TIMESTAMP, report_summary TEXT).
    """
    query = "INSERT INTO report_log (generated_at, report_summary) VALUES (NOW(), %s)"
    report_summary = json.dumps(report_data)
    with conn.cursor() as cur:
        cur.execute(query, (report_summary,))
        conn.commit()

# -------------------------------
# Main Execution
# -------------------------------
def main():
    # If you only want to parse and not generate a PDF, remove the second arg
    if len(sys.argv) < 2:
        print("Usage: python process_dna.py <input_dna_file.txt> [<output_report.pdf>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_pdf = None
    if len(sys.argv) > 2:
        output_pdf = sys.argv[2]

    # Parse the DNA file in Python
    parsed_snps = read_dna_file(input_file)
    print(f"Parsed {len(parsed_snps)} SNP records from the DNA file.")

    # Connect to the database
    try:
        conn = connect_to_database()
        print("Database connection established.")
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

    # Assemble all SNP-related data
    report_data = assemble_report_data(conn, parsed_snps)
    print("Report data assembled.")

    # If an output PDF path is provided, generate a PDF
    if output_pdf:
        generate_pdf(report_data, output_pdf)
        print(f"PDF report generated at: {output_pdf}")

        # Optionally log the report
        try:
            log_report_generation(conn, report_data)
            print("Report generation logged.")
        except Exception as e:
            print(f"Error logging report generation: {e}")

    conn.close()

if __name__ == "__main__":
    main()

