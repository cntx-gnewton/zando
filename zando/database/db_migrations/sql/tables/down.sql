
-- Drop all tables in reverse dependency order to prevent foreign key constraint issues

-- Product-related tables
DROP TABLE IF EXISTS public.product_genetic_suitability CASCADE;
DROP TABLE IF EXISTS public.product_routine_position CASCADE;
DROP TABLE IF EXISTS public.product_ingredient_link CASCADE;
DROP TABLE IF EXISTS public.product_concern_link CASCADE;
DROP TABLE IF EXISTS public.product_aspect_link CASCADE;
DROP TABLE IF EXISTS public.product_benefit_link CASCADE;
DROP TABLE IF EXISTS public.product_concern CASCADE;
DROP TABLE IF EXISTS public.product_aspect CASCADE;
DROP TABLE IF EXISTS public.product_benefit CASCADE;
DROP TABLE IF EXISTS public.product CASCADE;

-- Report-related tables
DROP TABLE IF EXISTS public.report_log CASCADE;
DROP TABLE IF EXISTS public.report_sections CASCADE;

-- Relationship tables (join tables)
DROP TABLE IF EXISTS public.characteristic_condition_link CASCADE;
DROP TABLE IF EXISTS public.condition_ingredient_link CASCADE;
DROP TABLE IF EXISTS public.snp_characteristic_link CASCADE;
DROP TABLE IF EXISTS public.snp_ingredient_link CASCADE;
DROP TABLE IF EXISTS public.snp_ingredientcaution_link CASCADE;

-- Core entity tables
DROP TABLE IF EXISTS public.ingredient CASCADE;
DROP TABLE IF EXISTS public.ingredientcaution CASCADE;
DROP TABLE IF EXISTS public.skincondition CASCADE;
DROP TABLE IF EXISTS public.skincharacteristic CASCADE;
DROP TABLE IF EXISTS public.snp CASCADE;