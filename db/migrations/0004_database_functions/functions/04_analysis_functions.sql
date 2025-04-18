-- Analysis Functions for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to get all characteristics related to a SNP
CREATE OR REPLACE FUNCTION get_snp_characteristics(snp_rsid TEXT)
RETURNS TABLE (
    characteristic_id INTEGER,
    characteristic_name TEXT,
    effect_direction TEXT,
    evidence_strength TEXT,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT sc.characteristic_id, sc.name, scl.effect_direction, scl.evidence_strength, sc.description
    FROM snp s
    JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    WHERE s.rsid = snp_rsid
    ORDER BY scl.evidence_strength, sc.name;
END;
$$ LANGUAGE plpgsql;

-- Function to get all ingredients beneficial for a SNP
CREATE OR REPLACE FUNCTION get_snp_beneficial_ingredients(snp_rsid TEXT)
RETURNS TABLE (
    ingredient_id INTEGER,
    ingredient_name TEXT,
    benefit_mechanism TEXT,
    recommendation_strength TEXT,
    evidence_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT i.ingredient_id, i.name, sil.benefit_mechanism, sil.recommendation_strength, sil.evidence_level
    FROM snp s
    JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
    JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
    WHERE s.rsid = snp_rsid
    ORDER BY sil.recommendation_strength, sil.evidence_level, i.name;
END;
$$ LANGUAGE plpgsql;

-- Function to get all ingredients to be cautious with for a SNP
CREATE OR REPLACE FUNCTION get_snp_caution_ingredients(snp_rsid TEXT)
RETURNS TABLE (
    caution_id INTEGER,
    ingredient_name TEXT,
    category TEXT,
    risk_mechanism TEXT,
    relationship_notes TEXT,
    evidence_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT ic.caution_id, ic.ingredient_name, ic.category, ic.risk_mechanism, 
           sicl.relationship_notes, sicl.evidence_level
    FROM snp s
    JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
    JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    WHERE s.rsid = snp_rsid
    ORDER BY sicl.evidence_level, ic.ingredient_name;
END;
$$ LANGUAGE plpgsql;

-- Function to get all conditions related to a characteristic
CREATE OR REPLACE FUNCTION get_characteristic_conditions(characteristic_name TEXT)
RETURNS TABLE (
    condition_id INTEGER,
    condition_name TEXT,
    description TEXT,
    relationship_type TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT sc.condition_id, sc.name, sc.description, ccl.relationship_type
    FROM skincharacteristic sc1
    JOIN characteristic_condition_link ccl ON sc1.characteristic_id = ccl.characteristic_id
    JOIN skincondition sc ON ccl.condition_id = sc.condition_id
    WHERE sc1.name = characteristic_name
    ORDER BY ccl.relationship_type, sc.name;
END;
$$ LANGUAGE plpgsql;