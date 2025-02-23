-- Test Suite for Skincare Genetics Database

-- 1. Check all tables exist and their row counts
SELECT 
    table_name, 
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name=tables.table_name) as column_count,
    (SELECT COUNT(*) FROM (SELECT * FROM ONLY pg_namespace n, pg_class c WHERE n.oid = c.relnamespace AND c.relname=tables.table_name) t) as row_count
FROM (
    VALUES 
        ('snp'),
        ('skincharacteristic'),
        ('skincondition'),
        ('ingredient'),
        ('ingredientcaution'),
        ('snp_characteristic_link'),
        ('characteristic_condition_link'),
        ('condition_ingredient_link'),
        ('snp_ingredient_link'),
        ('snp_ingredientcaution_link')
) as tables(table_name);

-- 2. Test SNP relationships
-- For a specific SNP (e.g., FLG variant), show all related information
SELECT 
    s.rsid,
    s.gene,
    s.category,
    s.evidence_strength,
    -- Related characteristics
    STRING_AGG(DISTINCT sc.name, ', ') as affected_characteristics,
    -- Related conditions
    STRING_AGG(DISTINCT cond.name, ', ') as related_conditions,
    -- Recommended ingredients
    STRING_AGG(DISTINCT i.name, ', ') as beneficial_ingredients,
    -- Ingredients to avoid
    STRING_AGG(DISTINCT ic.ingredient_name, ', ') as cautionary_ingredients
FROM snp s
LEFT JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
LEFT JOIN characteristic_condition_link ccl ON sc.characteristic_id = ccl.characteristic_id
LEFT JOIN skincondition cond ON ccl.condition_id = cond.condition_id
LEFT JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
LEFT JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
LEFT JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
WHERE s.rsid = 'rs61816761'  -- FLG variant
GROUP BY s.rsid, s.gene, s.category, s.evidence_strength;

-- 3. Test Ingredient Recommendations
-- Show all ingredients recommended for a specific condition
SELECT 
    sc.name as condition,
    STRING_AGG(DISTINCT 
        CASE 
            WHEN cil.recommendation_strength = 'First-line' THEN i.name
        END, 
        ', '
    ) as first_line_treatments,
    STRING_AGG(DISTINCT 
        CASE 
            WHEN cil.recommendation_strength = 'Second-line' THEN i.name
        END, 
        ', '
    ) as second_line_treatments
FROM skincondition sc
LEFT JOIN condition_ingredient_link cil ON sc.condition_id = cil.condition_id
LEFT JOIN ingredient i ON cil.ingredient_id = i.ingredient_id
GROUP BY sc.name;

-- 4. Test Ingredient Cautions
-- Show all SNPs and their related ingredient cautions
SELECT 
    s.gene,
    s.evidence_strength,
    COUNT(DISTINCT ic.ingredient_name) as num_cautions,
    STRING_AGG(DISTINCT ic.ingredient_name, ', ') as ingredients_to_avoid
FROM snp s
JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
GROUP BY s.gene, s.evidence_strength
ORDER BY s.evidence_strength DESC, num_cautions DESC;

-- 5. Test Complete Recommendation Path
-- Show the complete path from SNP → Characteristic → Condition → Ingredients
SELECT 
    s.gene,
    sc.name as characteristic,
    cond.name as condition,
    STRING_AGG(DISTINCT i.name, ', ') as recommended_ingredients,
    STRING_AGG(DISTINCT ic.ingredient_name, ', ') as avoid_ingredients
FROM snp s
JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
JOIN characteristic_condition_link ccl ON sc.characteristic_id = ccl.characteristic_id
JOIN skincondition cond ON ccl.condition_id = cond.condition_id
LEFT JOIN condition_ingredient_link cil ON cond.condition_id = cil.condition_id
LEFT JOIN ingredient i ON cil.ingredient_id = i.ingredient_id
LEFT JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
GROUP BY s.gene, sc.name, cond.name
ORDER BY s.gene, sc.name;
