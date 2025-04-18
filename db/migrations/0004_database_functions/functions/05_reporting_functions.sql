-- Reporting Functions for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to search across all entities (SNPs, characteristics, ingredients)
CREATE OR REPLACE FUNCTION global_search(search_term TEXT)
RETURNS TABLE (
    entity_type TEXT,
    entity_id INTEGER,
    name TEXT,
    description TEXT,
    relevance FLOAT
) AS $$
BEGIN
    -- Search SNPs
    RETURN QUERY
    SELECT 'snp' AS entity_type, s.snp_id AS entity_id, 
           s.rsid AS name, s.effect AS description, 
           CASE
               WHEN s.rsid = search_term THEN 1.0
               WHEN s.gene = search_term THEN 0.9
               WHEN s.rsid ILIKE '%' || search_term || '%' THEN 0.7
               ELSE 0.5
           END AS relevance
    FROM snp s
    WHERE s.rsid ILIKE '%' || search_term || '%'
    OR s.gene ILIKE '%' || search_term || '%'
    OR s.effect ILIKE '%' || search_term || '%';
    
    -- Search characteristics
    RETURN QUERY
    SELECT 'characteristic' AS entity_type, c.characteristic_id AS entity_id,
           c.name AS name, c.description AS description,
           CASE
               WHEN c.name ILIKE search_term THEN 1.0
               WHEN c.name ILIKE '%' || search_term || '%' THEN 0.8
               ELSE 0.5
           END AS relevance
    FROM skincharacteristic c
    WHERE c.name ILIKE '%' || search_term || '%'
    OR c.description ILIKE '%' || search_term || '%';
    
    -- Search ingredients
    RETURN QUERY
    SELECT 'ingredient' AS entity_type, i.ingredient_id AS entity_id,
           i.name AS name, i.mechanism AS description,
           CASE
               WHEN i.name ILIKE search_term THEN 1.0
               WHEN i.name ILIKE '%' || search_term || '%' THEN 0.8
               ELSE 0.5
           END AS relevance
    FROM ingredient i
    WHERE i.name ILIKE '%' || search_term || '%'
    OR i.mechanism ILIKE '%' || search_term || '%';
    
    -- Search conditions
    RETURN QUERY
    SELECT 'condition' AS entity_type, c.condition_id AS entity_id,
           c.name AS name, c.description AS description,
           CASE
               WHEN c.name ILIKE search_term THEN 1.0
               WHEN c.name ILIKE '%' || search_term || '%' THEN 0.8
               WHEN c.description ILIKE '%' || search_term || '%' THEN 0.6
               ELSE 0.4
           END AS relevance
    FROM skincondition c
    WHERE c.name ILIKE '%' || search_term || '%'
    OR c.description ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;

-- Function to generate ingredient recommendations based on a set of SNPs
CREATE OR REPLACE FUNCTION generate_ingredient_recommendations(rsids TEXT[])
RETURNS TABLE (
    ingredient_id INTEGER,
    ingredient_name TEXT,
    total_score FLOAT,
    affected_snps TEXT[],
    recommendation_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH snp_matches AS (
        SELECT s.snp_id, s.rsid, s.gene
        FROM snp s
        WHERE s.rsid = ANY(rsids)
    ),
    ingredient_scores AS (
        SELECT 
            i.ingredient_id,
            i.name AS ingredient_name,
            -- Calculate a score based on evidence level and recommendation strength
            SUM(
                CASE sil.evidence_level
                    WHEN 'Strong' THEN 3.0
                    WHEN 'Moderate' THEN 2.0
                    WHEN 'Weak' THEN 1.0
                    ELSE 0.5
                END *
                CASE sil.recommendation_strength
                    WHEN 'First-line' THEN 3.0
                    WHEN 'Second-line' THEN 2.0
                    WHEN 'Supportive' THEN 1.5
                    WHEN 'Adjuvant' THEN 1.0
                    ELSE 0.5
                END
            ) AS total_score,
            array_agg(DISTINCT sm.rsid) AS affected_snps
        FROM snp_matches sm
        JOIN snp_ingredient_link sil ON sm.snp_id = sil.snp_id
        JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
        GROUP BY i.ingredient_id, i.name
    )
    SELECT 
        is.ingredient_id,
        is.ingredient_name,
        is.total_score,
        is.affected_snps,
        CASE
            WHEN is.total_score >= 10.0 THEN 'Strongly Recommended'
            WHEN is.total_score >= 5.0 THEN 'Recommended'
            WHEN is.total_score >= 2.0 THEN 'Consider'
            ELSE 'Optional'
        END AS recommendation_level
    FROM ingredient_scores is
    ORDER BY is.total_score DESC, is.ingredient_name;
END;
$$ LANGUAGE plpgsql;

-- Function to generate caution ingredient list based on a set of SNPs
CREATE OR REPLACE FUNCTION generate_ingredient_cautions(rsids TEXT[])
RETURNS TABLE (
    ingredient_name TEXT,
    caution_category TEXT,
    risk_mechanism TEXT,
    total_caution_score FLOAT,
    affected_snps TEXT[],
    caution_level TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH snp_matches AS (
        SELECT s.snp_id, s.rsid, s.gene
        FROM snp s
        WHERE s.rsid = ANY(rsids)
    ),
    caution_scores AS (
        SELECT 
            ic.ingredient_name,
            ic.category AS caution_category,
            ic.risk_mechanism,
            -- Calculate a score based on evidence level
            SUM(
                CASE sicl.evidence_level
                    WHEN 'Strong' THEN 3.0
                    WHEN 'Moderate' THEN 2.0
                    WHEN 'Weak' THEN 1.0
                    ELSE 0.5
                END
            ) AS total_caution_score,
            array_agg(DISTINCT sm.rsid) AS affected_snps
        FROM snp_matches sm
        JOIN snp_ingredientcaution_link sicl ON sm.snp_id = sicl.snp_id
        JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
        GROUP BY ic.ingredient_name, ic.category, ic.risk_mechanism
    )
    SELECT 
        cs.ingredient_name,
        cs.caution_category,
        cs.risk_mechanism,
        cs.total_caution_score,
        cs.affected_snps,
        CASE
            WHEN cs.total_caution_score >= 6.0 THEN 'Avoid'
            WHEN cs.total_caution_score >= 3.0 THEN 'Use with Caution'
            ELSE 'Be Aware'
        END AS caution_level
    FROM caution_scores cs
    ORDER BY cs.total_caution_score DESC, cs.ingredient_name;
END;
$$ LANGUAGE plpgsql;