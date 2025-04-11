"""
Seed data for SNP records.

This module contains the SNP data extracted from the populate.sql file,
converted to a Python data structure for easier maintenance.
"""

def get_snps():
    """
    Returns a list of dictionaries containing SNP data.
    
    Each dictionary has the following keys:
    - rsid: The reference SNP ID (e.g., rs1805007)
    - gene: The associated gene (e.g., MC1R)
    - risk_allele: The allele associated with the effect
    - effect: Description of the SNP's effect
    - evidence_strength: Strong, Moderate, or Weak
    - category: The functional category (e.g., Pigmentation)
    
    Returns:
        List[Dict]: List of SNP dictionaries
    """
    return [
        # Pigmentation & Melanin Production - Strong Evidence
        {
            "rsid": "rs1805007", 
            "gene": "MC1R", 
            "risk_allele": "T", 
            "effect": "Associated with red hair, fair skin, and UV sensitivity", 
            "evidence_strength": "Strong", 
            "category": "Pigmentation"
        },
        {
            "rsid": "rs2228479", 
            "gene": "MC1R", 
            "risk_allele": "A", 
            "effect": "Affects UV response and pigmentation", 
            "evidence_strength": "Strong", 
            "category": "Pigmentation"
        },
        {
            "rsid": "rs1126809", 
            "gene": "TYR", 
            "risk_allele": "A", 
            "effect": "Affects melanin synthesis; linked to hyperpigmentation risk", 
            "evidence_strength": "Strong", 
            "category": "Pigmentation"
        },
        {
            "rsid": "rs16891982", 
            "gene": "SLC45A2", 
            "risk_allele": "G", 
            "effect": "Influences melanin production and pigmentation", 
            "evidence_strength": "Strong", 
            "category": "Pigmentation"
        },
        
        # Skin Hydration & Barrier Function - Strong Evidence
        {
            "rsid": "rs61816761", 
            "gene": "FLG", 
            "risk_allele": "A", 
            "effect": "Loss-of-function variant linked to eczema and dry skin", 
            "evidence_strength": "Strong", 
            "category": "Barrier Function"
        },
        
        # Inflammation & Immune Response - Strong Evidence
        {
            "rsid": "rs1800795", 
            "gene": "IL6", 
            "risk_allele": "C", 
            "effect": "Influences inflammatory response; linked to acne/rosacea", 
            "evidence_strength": "Strong", 
            "category": "Inflammation"
        },
        {
            "rsid": "rs361525", 
            "gene": "TNF-α", 
            "risk_allele": "A", 
            "effect": "Modulates inflammation; impacts conditions like psoriasis", 
            "evidence_strength": "Strong", 
            "category": "Inflammation"
        },
        {
            "rsid": "rs1800629", 
            "gene": "TNF-α", 
            "risk_allele": "A", 
            "effect": "Pro-inflammatory variant exacerbates acne severity", 
            "evidence_strength": "Strong", 
            "category": "Inflammation"
        },
        
        # Sun Sensitivity & DNA Repair - Moderate Evidence
        {
            "rsid": "rs13181", 
            "gene": "ERCC2", 
            "risk_allele": "C", 
            "effect": "Impacts DNA repair capacity; linked to melanoma risk", 
            "evidence_strength": "Moderate", 
            "category": "DNA Repair"
        },
        
        # Collagen Production & Skin Aging - Moderate Evidence
        {
            "rsid": "rs1799750", 
            "gene": "MMP1", 
            "risk_allele": "G", 
            "effect": "Affects collagen breakdown; linked to wrinkles and photoaging", 
            "evidence_strength": "Moderate", 
            "category": "Collagen"
        },
        {
            "rsid": "rs1800012", 
            "gene": "COL1A1", 
            "risk_allele": "T", 
            "effect": "Influences collagen type I synthesis; impacts skin elasticity", 
            "evidence_strength": "Moderate", 
            "category": "Collagen"
        },
        
        # Antioxidant Defense - Moderate Evidence
        {
            "rsid": "rs4880", 
            "gene": "SOD2", 
            "risk_allele": "G", 
            "effect": "Modulates oxidative stress response; impacts UV-induced damage", 
            "evidence_strength": "Moderate", 
            "category": "Antioxidant"
        },
        {
            "rsid": "rs1001179", 
            "gene": "CAT", 
            "risk_allele": "A", 
            "effect": "Affects catalase activity; linked to reduced antioxidant protection", 
            "evidence_strength": "Moderate", 
            "category": "Antioxidant"
        },
        
        # Acne Susceptibility - Weak Evidence
        {
            "rsid": "rs743572", 
            "gene": "CYP17A1", 
            "risk_allele": "A", 
            "effect": "Regulates androgen synthesis; influences sebum production", 
            "evidence_strength": "Weak", 
            "category": "Acne"
        },
        
        # Hormonal Influences - Weak Evidence
        {
            "rsid": "rs2234693", 
            "gene": "ESR1", 
            "risk_allele": "C", 
            "effect": "Estrogen receptor variant affecting skin thickness/hydration", 
            "evidence_strength": "Weak", 
            "category": "Hormonal"
        },
        
        # Ingredient Sensitivity - Weak Evidence
        {
            "rsid": "rs73341169", 
            "gene": "ALDH3A2", 
            "risk_allele": "A", 
            "effect": "Affects fatty aldehyde metabolism; linked to retinoid irritation", 
            "evidence_strength": "Weak", 
            "category": "Sensitivity"
        },
        {
            "rsid": "rs2068888", 
            "gene": "CYP26A1", 
            "risk_allele": "G", 
            "effect": "Influences retinoic acid metabolism; impacts retinoid efficacy", 
            "evidence_strength": "Weak", 
            "category": "Sensitivity"
        },
        
        # Rosacea & Vascular - Weak Evidence
        {
            "rsid": "rs17203410", 
            "gene": "HLA-DRA", 
            "risk_allele": "A", 
            "effect": "Immune-related variant associated with rosacea risk", 
            "evidence_strength": "Weak", 
            "category": "Rosacea"
        },
        {
            "rsid": "rs1799983", 
            "gene": "NOS3", 
            "risk_allele": "T", 
            "effect": "Affects nitric oxide production; influences flushing", 
            "evidence_strength": "Weak", 
            "category": "Vascular"
        },
        
        # Circadian Rhythm - Weak Evidence
        {
            "rsid": "rs1801260", 
            "gene": "CLOCK", 
            "risk_allele": "C", 
            "effect": "Affects skin repair cycles; impacts nighttime product efficacy", 
            "evidence_strength": "Weak", 
            "category": "Circadian"
        }
    ]