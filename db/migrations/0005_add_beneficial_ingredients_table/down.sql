-- Rollback for Beneficial Ingredients Views
-- Migration 0005: Removes the views and associated indexes

BEGIN;

-- Drop the views
DROP VIEW IF EXISTS public.snp_beneficial_ingredients;
DROP VIEW IF EXISTS public.snp_ingredient_cautions;

-- Drop the supporting indexes
DROP INDEX IF EXISTS idx_snp_ingredient_multi;
DROP INDEX IF EXISTS idx_snp_caution_multi;

COMMIT;