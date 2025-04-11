-- Add Beneficial Ingredients View
-- Migration 0005: Creates a view to expose beneficial ingredients data
-- Based on the original schema from initialize.sql

BEGIN;

-- Create the beneficial ingredients view for easier querying
CREATE OR REPLACE VIEW public.snp_beneficial_ingredients AS
SELECT 
    s.rsid,
    s.gene,
    s.category AS genetic_category,
    i.name AS ingredient_name,
    i.mechanism AS ingredient_mechanism,
    sil.benefit_mechanism,
    sil.recommendation_strength,
    sil.evidence_level
FROM 
    public.snp_ingredient_link sil
    JOIN public.snp s ON s.snp_id = sil.snp_id
    JOIN public.ingredient i ON i.ingredient_id = sil.ingredient_id
ORDER BY 
    sil.evidence_level DESC, 
    sil.recommendation_strength;

-- Create an index to improve performance of queries against the underlying tables
CREATE INDEX IF NOT EXISTS idx_snp_ingredient_multi 
ON public.snp_ingredient_link(snp_id, ingredient_id, evidence_level, recommendation_strength);

-- Also create the snp_ingredient_cautions view for completeness
CREATE OR REPLACE VIEW public.snp_ingredient_cautions AS
SELECT 
    s.rsid,
    s.gene,
    s.category AS genetic_category,
    ic.ingredient_name,
    ic.category AS caution_category,
    ic.risk_mechanism,
    sil.relationship_notes,
    sil.evidence_level
FROM 
    public.snp_ingredientcaution_link sil
    JOIN public.snp s ON s.snp_id = sil.snp_id
    JOIN public.ingredientcaution ic ON ic.caution_id = sil.caution_id
ORDER BY 
    sil.evidence_level DESC,
    ic.category;

-- Support index for caution queries
CREATE INDEX IF NOT EXISTS idx_snp_caution_multi
ON public.snp_ingredientcaution_link(snp_id, caution_id, evidence_level);

COMMIT;