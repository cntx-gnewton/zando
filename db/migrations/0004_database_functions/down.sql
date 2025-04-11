-- Down Migration for Database Functions
-- Migration 0004: Removing PostgreSQL functions

BEGIN;

-- ===============================
-- Remove all functions in reverse order
-- ===============================

-- Drop user management functions
DROP FUNCTION IF EXISTS log_user_action(INTEGER, TEXT, TEXT, INTEGER, TEXT, TEXT, JSONB);
DROP FUNCTION IF EXISTS authenticate_user(TEXT, TEXT);
DROP FUNCTION IF EXISTS register_user(TEXT, TEXT, TEXT, TEXT);

-- Drop reporting functions
DROP FUNCTION IF EXISTS generate_ingredient_cautions(TEXT[]);
DROP FUNCTION IF EXISTS generate_ingredient_recommendations(TEXT[]);
DROP FUNCTION IF EXISTS global_search(TEXT);
DROP FUNCTION IF EXISTS generate_analysis_summary(INTEGER, INTEGER, TEXT[]);

-- Drop analysis functions
DROP FUNCTION IF EXISTS get_characteristic_conditions(TEXT);
DROP FUNCTION IF EXISTS get_snp_caution_ingredients(TEXT);
DROP FUNCTION IF EXISTS get_snp_beneficial_ingredients(TEXT);
DROP FUNCTION IF EXISTS get_snp_characteristics(TEXT);

-- Drop search functions
DROP FUNCTION IF EXISTS search_ingredients(TEXT);
DROP FUNCTION IF EXISTS search_characteristics(TEXT);
DROP FUNCTION IF EXISTS search_snps(TEXT);

-- Drop utility functions
DROP FUNCTION IF EXISTS verify_password(TEXT, TEXT);
DROP FUNCTION IF EXISTS hash_password(TEXT);
DROP FUNCTION IF EXISTS generate_prefixed_uuid(TEXT);
DROP FUNCTION IF EXISTS update_timestamp();

-- Remove extensions if they're no longer needed
-- Note: In a real environment, you might want to check if these extensions
-- are used by other parts of the system before dropping them
-- DROP EXTENSION IF EXISTS pgcrypto;
-- DROP EXTENSION IF EXISTS "uuid-ossp";

COMMIT;