# dna_validator.py
import psycopg2
from psycopg2.extras import RealDictCursor

def validate_dna_analysis(file_path):
    """Validate DNA file analysis by checking genotypes and SNP detection."""
    
    # Read relevant SNPs from DNA file
    dna_data = {}
    print("\nReading DNA file...")
    with open(file_path, 'r') as file:
        start_processing = False
        for line in file:
            line = line.strip()
            if line == 'rsid\tchromosome\tposition\tallele1\tallele2':
                start_processing = True
                continue
            if start_processing and line and not line.startswith('#'):
                parts = line.split('\t')
                if len(parts) >= 5:  # Ensure we have all required fields
                    rsid = parts[0]
                    genotype = parts[3] + parts[4]  # Combine alleles
                    dna_data[rsid] = genotype

    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(
            dbname="algorythm",
            user="cam",
            host="localhost"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get relevant SNPs from database
        print("Checking SNPs in database...")
        cur.execute("""
            SELECT rsid, gene, risk_allele, category, evidence_strength 
            FROM snp 
            WHERE rsid = ANY(%s)
        """, (list(dna_data.keys()),))
        db_snps = cur.fetchall()

        # Print validation report
        print("\n=== DNA Analysis Validation Report ===\n")
        
        # 1. SNP Detection Stats
        print("SNP Detection Statistics:")
        print(f"Total SNPs in file: {len(dna_data)}")
        print(f"Relevant SNPs found: {len(db_snps)}")
        found_ratio = (len(db_snps) / len(dna_data)) * 100 if dna_data else 0
        print(f"Detection rate: {found_ratio:.2f}%")
        
        # 2. Detailed SNP Analysis
        print("\nDetailed SNP Analysis:")
        for snp in db_snps:
            rsid = snp['rsid']
            genotype = dna_data.get(rsid)
            risk_allele = snp['risk_allele']
            risk_status = 'Risk allele present' if risk_allele in genotype else 'No risk allele'
            risk_indicator = '⚠️' if risk_allele in genotype else '✓'
            
            print(f"\n{risk_indicator} SNP: {rsid} ({snp['gene']})")
            print(f"   Category: {snp['category']}")
            print(f"   Evidence: {snp['evidence_strength']}")
            print(f"   Your Genotype: {genotype}")
            print(f"   Risk Allele: {risk_allele}")
            print(f"   Status: {risk_status}")

        # 3. Coverage Analysis
        print("\nCoverage Analysis:")
        categories = {}
        for snp in db_snps:
            cat = snp['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"- {category}: {count} SNPs found")

        # 4. Data Quality Check
        print("\nData Quality Check:")
        valid_bases = {'A', 'T', 'C', 'G'}
        quality_issues = []
        
        for rsid, genotype in dna_data.items():
            if not all(base in valid_bases for base in genotype):
                quality_issues.append(f"Invalid bases in {rsid}: {genotype}")
        
        if quality_issues:
            print("Issues found:")
            for issue in quality_issues:
                print(f"- {issue}")
        else:
            print("✓ No data quality issues found")

        # 5. Evidence Level Distribution
        print("\nEvidence Level Distribution:")
        evidence_levels = {}
        for snp in db_snps:
            level = snp['evidence_strength']
            evidence_levels[level] = evidence_levels.get(level, 0) + 1
        
        for level, count in sorted(evidence_levels.items()):
            print(f"- {level}: {count} SNPs")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error during validation: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python dna_validator.py <path_to_dna_file>")
        sys.exit(1)
    
    validate_dna_analysis(sys.argv[1])
