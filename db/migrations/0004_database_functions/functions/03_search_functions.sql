-- Search Functions for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to search SNPs by rsid, gene, or effect
CREATE OR REPLACE FUNCTION search_snps(search_term TEXT)
RETURNS TABLE (
    snp_id INTEGER,
    rsid TEXT,
    gene TEXT,
    risk_allele TEXT,
    effect TEXT,
    evidence_strength TEXT,
    category TEXT,
    match_type TEXT,
    relevance FLOAT
) AS $$
BEGIN
    -- Search by exact rsid
    RETURN QUERY
    SELECT s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category,
           'exact_rsid' AS match_type, 1.0 AS relevance
    FROM snp s
    WHERE s.rsid = search_term;
    
    -- Search by gene
    RETURN QUERY
    SELECT s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category,
           'gene' AS match_type, 0.8 AS relevance
    FROM snp s
    WHERE s.gene ILIKE search_term;
    
    -- Search by effect using full-text search
    RETURN QUERY
    SELECT s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category,
           'effect_fulltext' AS match_type,
           ts_rank_cd(s.effect_tsv, plainto_tsquery('english', search_term)) AS relevance
    FROM snp s
    WHERE s.effect_tsv @@ plainto_tsquery('english', search_term)
    AND ts_rank_cd(s.effect_tsv, plainto_tsquery('english', search_term)) > 0.1;
    
    -- Search by partial rsid or gene
    RETURN QUERY
    SELECT s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category,
           'partial_match' AS match_type, 0.5 AS relevance
    FROM snp s
    WHERE s.rsid ILIKE '%' || search_term || '%'
    OR s.gene ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;

-- Function to search characteristics by name or description
CREATE OR REPLACE FUNCTION search_characteristics(search_term TEXT)
RETURNS TABLE (
    characteristic_id INTEGER,
    name TEXT,
    description TEXT,
    measurement_method TEXT,
    match_type TEXT,
    relevance FLOAT
) AS $$
BEGIN
    -- Search by exact name
    RETURN QUERY
    SELECT c.characteristic_id, c.name, c.description, c.measurement_method,
           'exact_name' AS match_type, 1.0 AS relevance
    FROM skincharacteristic c
    WHERE c.name ILIKE search_term;
    
    -- Search by description using full-text search
    RETURN QUERY
    SELECT c.characteristic_id, c.name, c.description, c.measurement_method,
           'description_fulltext' AS match_type,
           ts_rank_cd(c.description_tsv, plainto_tsquery('english', search_term)) AS relevance
    FROM skincharacteristic c
    WHERE c.description_tsv @@ plainto_tsquery('english', search_term)
    AND ts_rank_cd(c.description_tsv, plainto_tsquery('english', search_term)) > 0.1;
    
    -- Search by partial name
    RETURN QUERY
    SELECT c.characteristic_id, c.name, c.description, c.measurement_method,
           'partial_name' AS match_type, 0.7 AS relevance
    FROM skincharacteristic c
    WHERE c.name ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;

-- Function to search ingredients by name or mechanism
CREATE OR REPLACE FUNCTION search_ingredients(search_term TEXT)
RETURNS TABLE (
    ingredient_id INTEGER,
    name TEXT,
    mechanism TEXT,
    evidence_level TEXT,
    contraindications TEXT,
    match_type TEXT,
    relevance FLOAT
) AS $$
BEGIN
    -- Search by exact name
    RETURN QUERY
    SELECT i.ingredient_id, i.name, i.mechanism, i.evidence_level, i.contraindications,
           'exact_name' AS match_type, 1.0 AS relevance
    FROM ingredient i
    WHERE i.name ILIKE search_term;
    
    -- Search by mechanism using full-text search
    RETURN QUERY
    SELECT i.ingredient_id, i.name, i.mechanism, i.evidence_level, i.contraindications,
           'mechanism_fulltext' AS match_type,
           ts_rank_cd(i.mechanism_tsv, plainto_tsquery('english', search_term)) AS relevance
    FROM ingredient i
    WHERE i.mechanism_tsv @@ plainto_tsquery('english', search_term)
    AND ts_rank_cd(i.mechanism_tsv, plainto_tsquery('english', search_term)) > 0.1;
    
    -- Search by partial name
    RETURN QUERY
    SELECT i.ingredient_id, i.name, i.mechanism, i.evidence_level, i.contraindications,
           'partial_name' AS match_type, 0.7 AS relevance
    FROM ingredient i
    WHERE i.name ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;