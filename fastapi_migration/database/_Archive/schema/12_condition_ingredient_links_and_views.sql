-- Clear existing links if any
TRUNCATE TABLE Condition_Ingredient_Link;

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
