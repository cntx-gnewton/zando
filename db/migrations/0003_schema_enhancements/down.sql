-- Down migration for Schema Enhancements
-- Migration 0003: Reverting performance improvements and data integrity changes

BEGIN;

-- Drop triggers first
DROP TRIGGER IF EXISTS update_user_preference_timestamp ON user_preference;

-- Drop functions
DROP FUNCTION IF EXISTS update_timestamp();

-- Drop foreign key constraints
ALTER TABLE user_report DROP CONSTRAINT IF EXISTS fk_report_analysis;
ALTER TABLE user_analysis DROP CONSTRAINT IF EXISTS fk_analysis_file;

-- Drop user-related tables in correct order
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS user_preference;
DROP TABLE IF EXISTS user_report;
DROP TABLE IF EXISTS user_analysis;
DROP TABLE IF EXISTS user_dna_file;
DROP TABLE IF EXISTS app_user;

-- Remove full-text search capabilities
ALTER TABLE ingredient DROP COLUMN IF EXISTS mechanism_tsv;
ALTER TABLE skincharacteristic DROP COLUMN IF EXISTS description_tsv;
ALTER TABLE snp DROP COLUMN IF EXISTS effect_tsv;

-- Drop performance indexes
DROP INDEX IF EXISTS idx_snp_gene_cat;
DROP INDEX IF EXISTS idx_snp_evidence;
DROP INDEX IF EXISTS idx_characteristic_measurement;
DROP INDEX IF EXISTS idx_ingredient_evidence;
DROP INDEX IF EXISTS idx_ingredient_contraindications;
DROP INDEX IF EXISTS idx_caution_category;
DROP INDEX IF EXISTS idx_caution_affected;
DROP INDEX IF EXISTS idx_snp_char_effect;
DROP INDEX IF EXISTS idx_snp_ing_evidence;
DROP INDEX IF EXISTS idx_snp_caution_evidence;
DROP INDEX IF EXISTS idx_char_cond_relation;
DROP INDEX IF EXISTS idx_cond_ing_recommendation;
DROP INDEX IF EXISTS idx_snp_effect_tsv;
DROP INDEX IF EXISTS idx_characteristic_description_tsv;
DROP INDEX IF EXISTS idx_ingredient_mechanism_tsv;
DROP INDEX IF EXISTS idx_user_dna_file_user;
DROP INDEX IF EXISTS idx_user_dna_file_hash;
DROP INDEX IF EXISTS idx_user_analysis_user;
DROP INDEX IF EXISTS idx_user_analysis_created;
DROP INDEX IF EXISTS idx_user_analysis_json;
DROP INDEX IF EXISTS idx_user_report_user;
DROP INDEX IF EXISTS idx_user_report_created;
DROP INDEX IF EXISTS idx_audit_log_user;
DROP INDEX IF EXISTS idx_audit_log_action;
DROP INDEX IF EXISTS idx_audit_log_timestamp;

COMMIT;