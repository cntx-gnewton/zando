-- First, let's check the structure of our SNP table to ensure we match it
-- \d snp;

-- Clear existing data if needed
TRUNCATE TABLE snp CASCADE;
TRUNCATE TABLE skincharacteristic CASCADE;
TRUNCATE TABLE SNP_Characteristic_Link;
TRUNCATE TABLE SkinCondition CASCADE;
TRUNCATE TABLE Characteristic_Condition_Link;
TRUNCATE TABLE Ingredient CASCADE;
TRUNCATE TABLE IngredientCaution CASCADE;
TRUNCATE TABLE SNP_IngredientCaution_Link;
TRUNCATE TABLE SNP_Ingredient_Link;
TRUNCATE TABLE Condition_Ingredient_Link;


-- Strong Evidence SNPs
INSERT INTO snp (rsid, gene, risk_allele, effect, evidence_strength, category) VALUES
-- Pigmentation & Melanin Production
('rs1805007', 'MC1R', 'T', 'Associated with red hair, fair skin, and UV sensitivity', 'Strong', 'Pigmentation'),
('rs2228479', 'MC1R', 'A', 'Affects UV response and pigmentation', 'Strong', 'Pigmentation'),
('rs1126809', 'TYR', 'A', 'Affects melanin synthesis; linked to hyperpigmentation risk', 'Strong', 'Pigmentation'),
('rs16891982', 'SLC45A2', 'G', 'Influences melanin production and pigmentation', 'Strong', 'Pigmentation'),

-- Skin Hydration & Barrier Function
('rs61816761', 'FLG', 'A', 'Loss-of-function variant linked to eczema and dry skin', 'Strong', 'Barrier Function'),

-- Inflammation & Immune Response
('rs1800795', 'IL6', 'C', 'Influences inflammatory response; linked to acne/rosacea', 'Strong', 'Inflammation'),
('rs361525', 'TNF-α', 'A', 'Modulates inflammation; impacts conditions like psoriasis', 'Strong', 'Inflammation'),
('rs1800629', 'TNF-α', 'A', 'Pro-inflammatory variant exacerbates acne severity', 'Strong', 'Inflammation');

-- Moderate Evidence SNPs
INSERT INTO snp (rsid, gene, risk_allele, effect, evidence_strength, category) VALUES
-- Sun Sensitivity & DNA Repair
('rs13181', 'ERCC2', 'C', 'Impacts DNA repair capacity; linked to melanoma risk', 'Moderate', 'DNA Repair'),

-- Collagen Production & Skin Aging
('rs1799750', 'MMP1', 'G', 'Affects collagen breakdown; linked to wrinkles and photoaging', 'Moderate', 'Collagen'),
('rs1800012', 'COL1A1', 'T', 'Influences collagen type I synthesis; impacts skin elasticity', 'Moderate', 'Collagen'),

-- Antioxidant Defense
('rs4880', 'SOD2', 'G', 'Modulates oxidative stress response; impacts UV-induced damage', 'Moderate', 'Antioxidant'),
('rs1001179', 'CAT', 'A', 'Affects catalase activity; linked to reduced antioxidant protection', 'Moderate', 'Antioxidant');

-- Weak Evidence SNPs
INSERT INTO snp (rsid, gene, risk_allele, effect, evidence_strength, category) VALUES
-- Acne Susceptibility
('rs743572', 'CYP17A1', 'A', 'Regulates androgen synthesis; influences sebum production', 'Weak', 'Acne'),

-- Hormonal Influences
('rs2234693', 'ESR1', 'C', 'Estrogen receptor variant affecting skin thickness/hydration', 'Weak', 'Hormonal'),

-- Ingredient Sensitivity
('rs73341169', 'ALDH3A2', 'A', 'Affects fatty aldehyde metabolism; linked to retinoid irritation', 'Weak', 'Sensitivity'),
('rs2068888', 'CYP26A1', 'G', 'Influences retinoic acid metabolism; impacts retinoid efficacy', 'Weak', 'Sensitivity'),

-- Rosacea & Vascular
('rs17203410', 'HLA-DRA', 'A', 'Immune-related variant associated with rosacea risk', 'Weak', 'Rosacea'),
('rs1799983', 'NOS3', 'T', 'Affects nitric oxide production; influences flushing', 'Weak', 'Vascular'),

-- Circadian Rhythm
('rs1801260', 'CLOCK', 'C', 'Affects skin repair cycles; impacts nighttime product efficacy', 'Weak', 'Circadian');

-- Verify the data
-- SELECT category, evidence_strength, COUNT(*) 
-- FROM snp 
-- GROUP BY category, evidence_strength 
-- ORDER BY evidence_strength, category;



-- Insert core skin characteristics
INSERT INTO skincharacteristic (name, description, measurement_method) VALUES
-- Pigmentation related
('Melanin Production', 'Ability to produce and distribute melanin pigment in response to UV exposure', 'Spectrophotometry and colorimetry measurements'),
('UV Sensitivity', 'Susceptibility to UV-induced damage and sunburn', 'Minimal Erythema Dose (MED) testing'),

-- Barrier function related
('Barrier Function', 'Skin''s ability to retain moisture and protect against environmental stressors', 'Trans-epidermal water loss (TEWL) measurements'),
('Hydration Level', 'Moisture content in the stratum corneum', 'Corneometry measurements'),

-- Inflammation related
('Inflammatory Response', 'Tendency to develop inflammatory reactions in the skin', 'Clinical assessment and biomarker analysis'),
('Immune Activity', 'Immune system activity in the skin', 'Cytokine level measurements'),

-- Structural characteristics
('Collagen Production', 'Rate of new collagen synthesis', 'Biopsy analysis and ultrasound measurement'),
('Elastin Quality', 'Skin elasticity and recoil capacity', 'Cutometry measurements'),

-- Protective mechanisms
('Antioxidant Capacity', 'Ability to neutralize free radicals and oxidative stress', 'Free radical testing and antioxidant assays'),
('DNA Repair Capacity', 'Efficiency of repairing UV-induced DNA damage', 'Comet assay and DNA damage markers'),

-- Vascular characteristics
('Vascular Reactivity', 'Blood vessel response to stimuli and tendency for flushing', 'Laser Doppler flowmetry'),
('Microcirculation', 'Quality of blood flow in small skin vessels', 'Capillary microscopy'),

-- Other key characteristics
('Sebum Production', 'Rate and quality of natural oil production', 'Sebumeter measurements'),
('Product Sensitivity', 'Tendency to react to skincare ingredients', 'Patch testing and reactivity assessment'),
('Circadian Rhythm Response', 'Skin''s daily biological rhythm patterns', 'Time-dependent barrier function measurements');

-- Verify the data
-- SELECT name, LEFT(description, 50) as short_description, measurement_method 
-- FROM skincharacteristic 
-- ORDER BY name;

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


-- Insert skin conditions
INSERT INTO SkinCondition (name, description, severity_scale) VALUES
-- Barrier-related conditions
('Eczema', 'Chronic inflammatory skin condition causing dry, itchy, and inflamed skin patches', 'EASI (Eczema Area and Severity Index)'),
('Dry Skin', 'Reduced skin moisture and barrier dysfunction leading to rough, flaky skin', 'Clinician-rated 0-4 scale'),

-- Pigmentation conditions
('Hyperpigmentation', 'Excess melanin production causing dark patches or spots', 'MASI (Melasma Area and Severity Index)'),
('Photosensitivity', 'Increased sensitivity to UV radiation leading to sunburns and damage', 'Fitzpatrick Scale'),

-- Inflammatory conditions
('Acne', 'Inflammatory condition affecting sebaceous glands and hair follicles', 'IGA (Investigator''s Global Assessment) Scale'),
('Rosacea', 'Chronic inflammatory condition causing facial redness and bumps', 'IGA-RSS (Rosacea Severity Score)'),
('Psoriasis', 'Autoimmune condition causing rapid skin cell turnover and inflammation', 'PASI (Psoriasis Area Severity Index)'),

-- Aging-related conditions
('Photoaging', 'Premature aging due to UV exposure and environmental damage', 'Glogau Photoaging Scale'),
('Loss of Elasticity', 'Reduced skin firmness and elasticity due to collagen/elastin changes', 'Cutometer measurements'),

-- Sensitivity conditions
('Contact Dermatitis', 'Skin inflammation caused by contact with irritants or allergens', 'CDSI (Contact Dermatitis Severity Index)'),
('Product Sensitivity', 'Increased reactivity to skincare ingredients and products', 'RSSS (Reactive Skin Severity Score)'),

-- Vascular conditions
('Telangiectasia', 'Visible dilated blood vessels near skin surface', 'Modified IGA for telangiectasia'),
('Facial Flushing', 'Temporary redness due to vasodilation', 'Clinician-rated 0-3 scale');


-- Insert Characteristic-Condition relationships
INSERT INTO Characteristic_Condition_Link (characteristic_id, condition_id, relationship_type)
SELECT c.characteristic_id, sc.condition_id, 'Primary'
FROM skincharacteristic c, skincondition sc
WHERE 
    -- Barrier Function relationships
    (c.name = 'Barrier Function' AND sc.name IN ('Eczema', 'Dry Skin', 'Contact Dermatitis'))
    OR
    -- Hydration Level relationships
    (c.name = 'Hydration Level' AND sc.name IN ('Dry Skin', 'Eczema'))
    OR
    -- Melanin Production relationships
    (c.name = 'Melanin Production' AND sc.name IN ('Hyperpigmentation', 'Photosensitivity'))
    OR
    -- UV Sensitivity relationships
    (c.name = 'UV Sensitivity' AND sc.name IN ('Photosensitivity', 'Photoaging'))
    OR
    -- Inflammatory Response relationships
    (c.name = 'Inflammatory Response' AND sc.name IN ('Acne', 'Rosacea', 'Psoriasis', 'Contact Dermatitis'))
    OR
    -- Immune Activity relationships
    (c.name = 'Immune Activity' AND sc.name IN ('Psoriasis', 'Contact Dermatitis'))
    OR
    -- Collagen Production relationships
    (c.name = 'Collagen Production' AND sc.name IN ('Photoaging', 'Loss of Elasticity'))
    OR
    -- Elastin Quality relationships
    (c.name = 'Elastin Quality' AND sc.name = 'Loss of Elasticity')
    OR
    -- Antioxidant Capacity relationships
    (c.name = 'Antioxidant Capacity' AND sc.name IN ('Photoaging', 'Photosensitivity'))
    OR
    -- Vascular Reactivity relationships
    (c.name = 'Vascular Reactivity' AND sc.name IN ('Facial Flushing', 'Telangiectasia', 'Rosacea'))
    OR
    -- Microcirculation relationships
    (c.name = 'Microcirculation' AND sc.name IN ('Telangiectasia', 'Facial Flushing'))
    OR
    -- Product Sensitivity relationships
    (c.name = 'Product Sensitivity' AND sc.name IN ('Contact Dermatitis', 'Product Sensitivity'));

-- Add secondary relationships
INSERT INTO Characteristic_Condition_Link (characteristic_id, condition_id, relationship_type)
SELECT c.characteristic_id, sc.condition_id, 'Secondary'
FROM skincharacteristic c, skincondition sc
WHERE 
    -- Secondary relationships for Inflammatory Response
    (c.name = 'Inflammatory Response' AND sc.name IN ('Hyperpigmentation', 'Loss of Elasticity'))
    OR
    -- Secondary relationships for Barrier Function
    (c.name = 'Barrier Function' AND sc.name IN ('Acne', 'Rosacea'))
    OR
    -- Secondary relationships for Antioxidant Capacity
    (c.name = 'Antioxidant Capacity' AND sc.name IN ('Loss of Elasticity', 'Hyperpigmentation'));



-- Insert ingredients
INSERT INTO Ingredient (name, mechanism, evidence_level, contraindications) VALUES
-- Barrier Function & Hydration
('Ceramides', 'Restore and strengthen skin barrier function by replacing natural lipids', 'Strong', 'None known'),
('Hyaluronic Acid', 'Hydrates by binding water molecules in the skin', 'Strong', 'None significant'),
('Niacinamide', 'Supports barrier function, reduces inflammation, regulates sebum', 'Strong', 'Rare flushing in sensitive individuals'),
('Squalane', 'Emollient that mimics skin''s natural oils', 'Moderate', 'None known'),

-- Antioxidants & Protection
('Vitamin C (L-Ascorbic Acid)', 'Antioxidant, collagen synthesis support, brightening', 'Strong', 'Can be irritating at high concentrations'),
('Vitamin E (Tocopherol)', 'Antioxidant, moisturizing, strengthens skin barrier', 'Strong', 'May cause contact dermatitis in some'),
('Green Tea Extract', 'Antioxidant, anti-inflammatory, photoprotective', 'Moderate', 'None significant'),
('Resveratrol', 'Antioxidant, anti-aging, protects against UV damage', 'Moderate', 'May increase sensitivity to retinoids'),

-- Cell Turnover & Anti-aging
('Retinoids', 'Increase cell turnover, stimulate collagen, reduce pigmentation', 'Strong', 'Pregnancy, sun sensitivity, initial irritation'),
('Peptides', 'Signal collagen production, improve skin firmness', 'Moderate', 'None significant'),
('Glycolic Acid', 'Exfoliates, improves texture, stimulates collagen', 'Strong', 'Sun sensitivity, may irritate sensitive skin'),
('Lactic Acid', 'Gentle exfoliation, hydration, improves texture', 'Strong', 'May cause temporary sensitivity'),

-- Pigmentation
('Kojic Acid', 'Inhibits tyrosinase, reduces melanin production', 'Moderate', 'May cause skin irritation'),
('Vitamin B12', 'Reduces hyperpigmentation, supports cell renewal', 'Moderate', 'None significant'),
('Arbutin', 'Natural tyrosinase inhibitor, reduces pigmentation', 'Strong', 'None significant'),
('Tranexamic Acid', 'Reduces melanin production and inflammation', 'Strong', 'Rare allergic reactions'),

-- Anti-inflammatory
('Centella Asiatica', 'Calms inflammation, supports healing', 'Strong', 'Rare allergic reactions'),
('Zinc Oxide', 'Soothes skin, provides UV protection', 'Strong', 'None significant'),
('Colloidal Oatmeal', 'Reduces inflammation, supports barrier function', 'Strong', 'Rare cereal allergies'),
('Aloe Vera', 'Soothes inflammation, provides hydration', 'Moderate', 'Rare allergic reactions'),

-- Specialized Actives
('Azelaic Acid', 'Anti-inflammatory, reduces pigmentation and acne', 'Strong', 'Initial tingling sensation'),
('Bakuchiol', 'Natural retinol alternative, gentler cell turnover', 'Moderate', 'None significant'),
('Polyglutamic Acid', 'Superior hydration, supports barrier function', 'Moderate', 'None known'),
('Beta Glucan', 'Soothes, strengthens barrier, supports healing', 'Moderate', 'None significant');


-- Populate with ingredients to avoid or use with caution
INSERT INTO IngredientCaution (ingredient_name, category, risk_mechanism, affected_characteristic, alternative_ingredients) VALUES
-- Retinoid Metabolism Issues (associated with ALDH3A2, CYP26A1 variants)
('Retinol', 'Use with Caution', 'May cause increased irritation in individuals with retinoid metabolism variants', 'Product Sensitivity', 'Bakuchiol, Peptides'),
('Tretinoin', 'Use with Caution', 'Higher risk of irritation in retinoid metabolism variant carriers', 'Product Sensitivity', 'Bakuchiol, Niacinamide'),

-- Barrier Function Issues (associated with FLG variants)
('Sodium Lauryl Sulfate', 'Avoid', 'Disrupts barrier function, particularly risky with FLG mutations', 'Barrier Function', 'Gentle sulfate-free cleansers'),
('Denatured Alcohol', 'Avoid', 'Can severely compromise impaired skin barrier', 'Barrier Function', 'Glycerin, Butylene Glycol'),
('Essential Oils', 'Use with Caution', 'May irritate sensitive or barrier-compromised skin', 'Barrier Function', 'Fragrance-free alternatives'),

-- Inflammation Risk (associated with IL6, TNF-α variants)
('High-concentration AHAs', 'Use with Caution', 'May trigger excessive inflammation in sensitive individuals', 'Inflammatory Response', 'PHAs, low concentration lactic acid'),
('Benzoyl Peroxide', 'Use with Caution', 'Can cause increased inflammation in sensitive skin', 'Inflammatory Response', 'Azelaic Acid, Niacinamide'),

-- Pigmentation Risk (associated with MC1R, TYR variants)
('Hydroquinone', 'Use with Caution', 'May cause paradoxical hyperpigmentation in some individuals', 'Melanin Production', 'Kojic Acid, Vitamin C, Arbutin'),
('Bergamot Oil', 'Avoid', 'Can cause photosensitivity and irregular pigmentation', 'UV Sensitivity', 'Photostable botanical extracts'),

-- Oxidative Stress Sensitivity (associated with SOD2, CAT variants)
('High-concentration Vitamin C', 'Use with Caution', 'May cause oxidative stress in sensitive individuals', 'Antioxidant Capacity', 'Lower concentrations, stable derivatives'),
('Unstable Antioxidants', 'Avoid', 'Can become pro-oxidant in certain conditions', 'Antioxidant Capacity', 'Stable antioxidant formulations'),

-- Vascular Reactivity (associated with NOS3 variants)
('Menthol', 'Use with Caution', 'Can trigger vasodilation and flushing', 'Vascular Reactivity', 'Centella Asiatica, Allantoin'),
('Peppermint Oil', 'Use with Caution', 'May increase facial flushing', 'Vascular Reactivity', 'Chamomile, Green Tea Extract'),

-- General Sensitivity (multiple genetic factors)
('Synthetic Fragrances', 'Use with Caution', 'Common trigger for sensitive skin reactions', 'Product Sensitivity', 'Fragrance-free formulations'),
('Chemical Sunscreen Filters', 'Use with Caution', 'May cause reactions in sensitive individuals', 'UV Sensitivity', 'Mineral sunscreens');


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


-- Insert Condition-Ingredient relationships
INSERT INTO Condition_Ingredient_Link 
    (condition_id, ingredient_id, recommendation_strength, guidance_notes)
SELECT 
    sc.condition_id,
    i.ingredient_id,
    CASE 
        WHEN i.evidence_level = 'Strong' THEN 'First-line'
        WHEN i.evidence_level = 'Moderate' THEN 'Second-line'
        ELSE 'Adjuvant'
    END as recommendation_strength,
    'Recommended based on clinical evidence for ' || sc.name
FROM skincondition sc, ingredient i
WHERE 
    -- Eczema treatments
    (sc.name = 'Eczema' AND i.name IN 
        ('Ceramides', 'Colloidal Oatmeal', 'Hyaluronic Acid', 'Niacinamide'))
    OR
    -- Hyperpigmentation treatments
    (sc.name = 'Hyperpigmentation' AND i.name IN 
        ('Vitamin C (L-Ascorbic Acid)', 'Niacinamide', 'Arbutin', 'Kojic Acid', 'Tranexamic Acid'))
    OR
    -- Acne treatments
    (sc.name = 'Acne' AND i.name IN 
        ('Niacinamide', 'Azelaic Acid', 'Green Tea Extract', 'Zinc Oxide'))
    OR
    -- Photoaging treatments
    (sc.name = 'Photoaging' AND i.name IN 
        ('Retinoids', 'Vitamin C (L-Ascorbic Acid)', 'Peptides', 'Vitamin E (Tocopherol)'))
    OR
    -- Rosacea treatments
    (sc.name = 'Rosacea' AND i.name IN 
        ('Centella Asiatica', 'Niacinamide', 'Azelaic Acid', 'Green Tea Extract'))
    OR
    -- Loss of Elasticity treatments
    (sc.name = 'Loss of Elasticity' AND i.name IN 
        ('Peptides', 'Retinoids', 'Vitamin C (L-Ascorbic Acid)', 'Bakuchiol'))
    OR
    -- Contact Dermatitis treatments
    (sc.name = 'Contact Dermatitis' AND i.name IN 
        ('Colloidal Oatmeal', 'Centella Asiatica', 'Beta Glucan', 'Aloe Vera'))
    OR
    -- Dry Skin treatments
    (sc.name = 'Dry Skin' AND i.name IN 
        ('Ceramides', 'Hyaluronic Acid', 'Squalane', 'Polyglutamic Acid'));

-- Create a view for comprehensive skincare recommendations
CREATE OR REPLACE VIEW comprehensive_recommendations AS
SELECT 
    s.rsid,
    s.gene,
    s.category as genetic_category,
    sc.name as condition,
    i.name as recommended_ingredient,
    i.mechanism as ingredient_mechanism,
    cil.recommendation_strength,
    sil.benefit_mechanism,
    ic.ingredient_name as ingredients_to_avoid,
    ic.risk_mechanism
FROM snp s
JOIN SNP_Characteristic_Link scl ON s.snp_id = scl.snp_id
JOIN Characteristic_Condition_Link ccl ON scl.characteristic_id = ccl.characteristic_id
JOIN skincondition sc ON ccl.condition_id = sc.condition_id
JOIN Condition_Ingredient_Link cil ON sc.condition_id = cil.condition_id
JOIN ingredient i ON cil.ingredient_id = i.ingredient_id
LEFT JOIN SNP_Ingredient_Link sil ON s.snp_id = sil.snp_id AND i.ingredient_id = sil.ingredient_id
LEFT JOIN SNP_IngredientCaution_Link sicl ON s.snp_id = sicl.snp_id
LEFT JOIN IngredientCaution ic ON sicl.caution_id = ic.caution_id;
