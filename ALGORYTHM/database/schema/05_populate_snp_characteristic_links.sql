-- Clear existing data if needed
TRUNCATE TABLE SNP_Characteristic_Link;

-- Insert SNP-Characteristic relationships
INSERT INTO SNP_Characteristic_Link (snp_id, characteristic_id, effect_direction, evidence_strength)
SELECT s.snp_id, c.characteristic_id, 'Modulates', s.evidence_strength
FROM snp s, skincharacteristic c
WHERE 
    -- MC1R variants
    (s.gene = 'MC1R' AND c.name IN ('Melanin Production', 'UV Sensitivity'))
    OR
    -- TYR variant
    (s.gene = 'TYR' AND c.name = 'Melanin Production')
    OR
    -- SLC45A2 variant
    (s.gene = 'SLC45A2' AND c.name = 'Melanin Production')
    OR
    -- FLG variant
    (s.gene = 'FLG' AND c.name IN ('Barrier Function', 'Hydration Level'))
    OR
    -- IL6 and TNF-α variants
    (s.gene IN ('IL6', 'TNF-α') AND c.name IN ('Inflammatory Response', 'Immune Activity'))
    OR
    -- ERCC2 variant
    (s.gene = 'ERCC2' AND c.name = 'DNA Repair Capacity')
    OR
    -- MMP1 and COL1A1 variants
    (s.gene IN ('MMP1', 'COL1A1') AND c.name IN ('Collagen Production', 'Elastin Quality'))
    OR
    -- SOD2 and CAT variants
    (s.gene IN ('SOD2', 'CAT') AND c.name = 'Antioxidant Capacity')
    OR
    -- CYP17A1 variant
    (s.gene = 'CYP17A1' AND c.name = 'Sebum Production')
    OR
    -- ESR1 variant
    (s.gene = 'ESR1' AND c.name IN ('Collagen Production', 'Hydration Level'))
    OR
    -- ALDH3A2 and CYP26A1 variants
    (s.gene IN ('ALDH3A2', 'CYP26A1') AND c.name = 'Product Sensitivity')
    OR
    -- NOS3 variant
    (s.gene = 'NOS3' AND c.name IN ('Vascular Reactivity', 'Microcirculation'))
    OR
    -- CLOCK variant
    (s.gene = 'CLOCK' AND c.name = 'Circadian Rhythm Response');

-- Update specific effect directions
UPDATE SNP_Characteristic_Link
SET effect_direction = 'Decreases'
WHERE snp_id IN (SELECT snp_id FROM snp WHERE gene = 'FLG')
  AND characteristic_id IN (SELECT characteristic_id FROM skincharacteristic WHERE name IN ('Barrier Function', 'Hydration Level'));

UPDATE SNP_Characteristic_Link
SET effect_direction = 'Increases'
WHERE snp_id IN (SELECT snp_id FROM snp WHERE gene IN ('IL6', 'TNF-α'))
  AND characteristic_id IN (SELECT characteristic_id FROM skincharacteristic WHERE name = 'Inflammatory Response');

-- Verify the relationships
SELECT 
    s.gene,
    s.rsid,
    s.evidence_strength,
    c.name as characteristic,
    scl.effect_direction
FROM SNP_Characteristic_Link scl
JOIN snp s ON s.snp_id = scl.snp_id
JOIN skincharacteristic c ON c.characteristic_id = scl.characteristic_id
ORDER BY s.evidence_strength, s.gene, c.name;
