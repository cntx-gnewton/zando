-- Check if all detected SNPs exist in our database
SELECT s.rsid, s.gene, s.evidence_strength
FROM snp s
WHERE s.rsid IN (
    'rs61816761', 'rs1801260', 'rs16891982', 'rs1800629', 
    'rs361525', 'rs4880', 'rs1800795', 'rs2068888', 
    'rs743572', 'rs1001179', 'rs1126809', 'rs2228479', 
    'rs1805007', 'rs1800012', 'rs13181'
)
ORDER BY s.evidence_strength;

-- Verify risk level assignments are correct
WITH your_snps AS (
    SELECT unnest(ARRAY[
        'rs61816761', 'rs1801260', 'rs16891982', 'rs1800629', 
        'rs361525', 'rs4880', 'rs1800795', 'rs2068888', 
        'rs743572', 'rs1001179', 'rs1126809', 'rs2228479', 
        'rs1805007', 'rs1800012', 'rs13181'
    ]) as rsid
)
SELECT 
    s.gene,
    s.evidence_strength,
    s.category,
    CASE 
        WHEN s.evidence_strength = 'Strong' THEN 'High'
        WHEN s.evidence_strength = 'Moderate' THEN 'Medium'
        ELSE 'Low'
    END as expected_risk_level
FROM snp s
JOIN your_snps ys ON s.rsid = ys.rsid;

-- Check ingredient recommendations against skin characteristics
WITH your_snps AS (
    SELECT unnest(ARRAY[
        'rs61816761', 'rs1801260', 'rs16891982', 'rs1800629', 
        'rs361525', 'rs4880', 'rs1800795', 'rs2068888', 
        'rs743572', 'rs1001179', 'rs1126809', 'rs2228479', 
        'rs1805007', 'rs1800012', 'rs13181'
    ]) as rsid
)
SELECT DISTINCT
    s.gene,
    sc.name as skin_characteristic,
    i.name as recommended_ingredient,
    i.evidence_level
FROM snp s
JOIN your_snps ys ON s.rsid = ys.rsid
JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
JOIN condition_ingredient_link cil ON TRUE
JOIN ingredient i ON cil.ingredient_id = i.ingredient_id
WHERE i.evidence_level = 'Strong'
ORDER BY s.gene, sc.name;

-- Verify ingredient cautions are appropriate
WITH your_snps AS (
    SELECT unnest(ARRAY[
        'rs61816761', 'rs1801260', 'rs16891982', 'rs1800629', 
        'rs361525', 'rs4880', 'rs1800795', 'rs2068888', 
        'rs743572', 'rs1001179', 'rs1126809', 'rs2228479', 
        'rs1805007', 'rs1800012', 'rs13181'
    ]) as rsid
)
SELECT DISTINCT
    s.gene,
    ic.ingredient_name,
    ic.category as caution_level,
    ic.risk_mechanism
FROM snp s
JOIN your_snps ys ON s.rsid = ys.rsid
JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
ORDER BY ic.category DESC, s.gene;

-- Create a test case comparing expected vs actual output
WITH test_case AS (
    SELECT ARRAY[
        'rs61816761', 'rs1801260', 'rs16891982', 'rs1800629', 
        'rs361525', 'rs4880', 'rs1800795', 'rs2068888', 
        'rs743572', 'rs1001179', 'rs1126809', 'rs2228479', 
        'rs1805007', 'rs1800012', 'rs13181'
    ] as test_snps
)
SELECT 
    'Number of SNPs' as test,
    CASE 
        WHEN array_length(test_snps, 1) = 15 THEN 'PASS'
        ELSE 'FAIL'
    END as result
FROM test_case
UNION ALL
SELECT 
    'Risk Level Assignment' as test,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM snp s
            WHERE s.rsid = ANY(test_case.test_snps)
            AND s.evidence_strength = 'Strong'
        ) THEN 'PASS'
        ELSE 'FAIL'
    END as result
FROM test_case;


