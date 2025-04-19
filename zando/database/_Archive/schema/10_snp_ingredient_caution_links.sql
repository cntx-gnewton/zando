-- Clear existing links if any
TRUNCATE TABLE SNP_IngredientCaution_Link;

-- Insert SNP-IngredientCaution relationships
INSERT INTO SNP_IngredientCaution_Link (snp_id, caution_id, evidence_level, notes)
SELECT s.snp_id, ic.caution_id, 
    CASE 
        WHEN s.evidence_strength = 'Strong' THEN 'Strong'
        WHEN s.evidence_strength = 'Moderate' THEN 'Moderate'
        ELSE 'Weak'
    END as evidence_level,
    'Based on genetic variation affecting ' || s.category || ' pathway'
FROM snp s, IngredientCaution ic
WHERE 
    -- Retinoid Metabolism SNPs
    (s.gene IN ('ALDH3A2', 'CYP26A1') AND ic.ingredient_name IN ('Retinol', 'Tretinoin'))
    OR
    -- Barrier Function SNPs
    (s.gene = 'FLG' AND ic.ingredient_name IN ('Sodium Lauryl Sulfate', 'Denatured Alcohol', 'Essential Oils'))
    OR
    -- Inflammation SNPs
    (s.gene IN ('IL6', 'TNF-α') AND ic.ingredient_name IN ('High-concentration AHAs', 'Benzoyl Peroxide'))
    OR
    -- Pigmentation SNPs
    (s.gene IN ('MC1R', 'TYR') AND ic.ingredient_name IN ('Hydroquinone', 'Bergamot Oil'))
    OR
    -- Oxidative Stress SNPs
    (s.gene IN ('SOD2', 'CAT') AND ic.ingredient_name IN ('High-concentration Vitamin C', 'Unstable Antioxidants'))
    OR
    -- Vascular Reactivity SNPs
    (s.gene = 'NOS3' AND ic.ingredient_name IN ('Menthol', 'Peppermint Oil'));

-- Add general sensitivity links
INSERT INTO SNP_IngredientCaution_Link (snp_id, caution_id, evidence_level, notes)
SELECT s.snp_id, ic.caution_id, s.evidence_strength,
    'General sensitivity consideration based on ' || s.category || ' impact'
FROM snp s, IngredientCaution ic
WHERE s.category IN ('Barrier Function', 'Inflammation', 'Sensitivity')
    AND ic.ingredient_name IN ('Synthetic Fragrances', 'Chemical Sunscreen Filters');

-- Verify the relationships
SELECT 
    s.gene,
    s.rsid,
    s.evidence_strength,
    ic.ingredient_name,
    ic.category as caution_level,
    ic.affected_characteristic,
    scl.notes
FROM SNP_IngredientCaution_Link scl
JOIN snp s ON s.snp_id = scl.snp_id
JOIN IngredientCaution ic ON ic.caution_id = scl.caution_id
ORDER BY s.evidence_strength DESC, s.gene, ic.ingredient_name;

-- Create a view for easy querying of ingredient cautions by SNP
CREATE OR REPLACE VIEW snp_ingredient_cautions AS
SELECT 
    s.rsid,
    s.gene,
    s.category as genetic_category,
    s.evidence_strength as genetic_evidence,
    ic.ingredient_name,
    ic.category as caution_level,
    ic.risk_mechanism,
    ic.alternative_ingredients
FROM SNP_IngredientCaution_Link scl
JOIN snp s ON s.snp_id = scl.snp_id
JOIN IngredientCaution ic ON ic.caution_id = scl.caution_id;
