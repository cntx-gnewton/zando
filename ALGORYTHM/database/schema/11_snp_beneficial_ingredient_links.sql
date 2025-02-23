-- Create new linking table for SNPs and beneficial ingredients
CREATE TABLE IF NOT EXISTS SNP_Ingredient_Link (
    snp_id INTEGER REFERENCES snp(snp_id),
    ingredient_id INTEGER REFERENCES Ingredient(ingredient_id),
    benefit_mechanism TEXT,
    recommendation_strength VARCHAR CHECK (recommendation_strength IN ('First-line', 'Second-line', 'Supportive')),
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    PRIMARY KEY (snp_id, ingredient_id)
);

-- Insert SNP-Ingredient beneficial relationships
INSERT INTO SNP_Ingredient_Link (snp_id, ingredient_id, benefit_mechanism, recommendation_strength, evidence_level)
SELECT DISTINCT s.snp_id, i.ingredient_id,
    CASE 
        WHEN s.gene IN ('MC1R', 'TYR') THEN 'Supports melanin regulation and UV protection'
        WHEN s.gene = 'FLG' THEN 'Strengthens barrier function and hydration'
        WHEN s.gene IN ('IL6', 'TNF-α') THEN 'Reduces inflammation and soothes skin'
        WHEN s.gene IN ('MMP1', 'COL1A1') THEN 'Supports collagen production and skin structure'
        WHEN s.gene IN ('SOD2', 'CAT') THEN 'Provides antioxidant support'
        ELSE 'Supports overall skin health'
    END as benefit_mechanism,
    CASE
        WHEN s.evidence_strength = 'Strong' THEN 'First-line'
        WHEN s.evidence_strength = 'Moderate' THEN 'Second-line'
        ELSE 'Supportive'
    END as recommendation_strength,
    s.evidence_strength as evidence_level
FROM snp s
CROSS JOIN Ingredient i
WHERE 
    -- Pigmentation genes (MC1R, TYR) -> UV protection and pigmentation regulation
    (s.gene IN ('MC1R', 'TYR') AND i.name IN 
        ('Vitamin C (L-Ascorbic Acid)', 'Niacinamide', 'Arbutin', 'Tranexamic Acid', 'Zinc Oxide'))
    OR
    -- Barrier function gene (FLG) -> Barrier repair and hydration
    (s.gene = 'FLG' AND i.name IN 
        ('Ceramides', 'Hyaluronic Acid', 'Squalane', 'Colloidal Oatmeal', 'Polyglutamic Acid'))
    OR
    -- Inflammation genes (IL6, TNF-α) -> Anti-inflammatory
    (s.gene IN ('IL6', 'TNF-α') AND i.name IN 
        ('Niacinamide', 'Centella Asiatica', 'Zinc Oxide', 'Green Tea Extract', 'Azelaic Acid'))
    OR
    -- Collagen genes (MMP1, COL1A1) -> Collagen support
    (s.gene IN ('MMP1', 'COL1A1') AND i.name IN 
        ('Retinoids', 'Peptides', 'Vitamin C (L-Ascorbic Acid)', 'Bakuchiol'))
    OR
    -- Antioxidant genes (SOD2, CAT) -> Antioxidant support
    (s.gene IN ('SOD2', 'CAT') AND i.name IN 
        ('Vitamin C (L-Ascorbic Acid)', 'Vitamin E (Tocopherol)', 'Resveratrol', 'Green Tea Extract'));

-- Create a view for easy querying of beneficial ingredients by SNP
CREATE OR REPLACE VIEW snp_beneficial_ingredients AS
SELECT 
    s.rsid,
    s.gene,
    s.category as genetic_category,
    i.name as ingredient_name,
    i.mechanism as ingredient_mechanism,
    sil.benefit_mechanism,
    sil.recommendation_strength,
    sil.evidence_level
FROM SNP_Ingredient_Link sil
JOIN snp s ON s.snp_id = sil.snp_id
JOIN Ingredient i ON i.ingredient_id = sil.ingredient_id
ORDER BY sil.evidence_level DESC, sil.recommendation_strength;
