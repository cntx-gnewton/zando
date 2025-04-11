-- Index Creation for Zando Genomic Analysis
-- Part of Migration 0003

BEGIN;

-- This file contains all indexes created in migration 0003
-- It's kept separate for documentation and maintenance purposes
-- These indexes are also included in up.sql and will be properly tracked

-- SNP Table Indexes
CREATE INDEX IF NOT EXISTS idx_snp_gene_cat ON snp(gene, category);
CREATE INDEX IF NOT EXISTS idx_snp_evidence ON snp(evidence_strength);

-- SkinCharacteristic Indexes
CREATE INDEX IF NOT EXISTS idx_characteristic_measurement ON skincharacteristic(measurement_method);

-- Ingredient Indexes
CREATE INDEX IF NOT EXISTS idx_ingredient_evidence ON ingredient(evidence_level);
CREATE INDEX IF NOT EXISTS idx_ingredient_contraindications ON ingredient(contraindications text_pattern_ops);

-- IngredientCaution Indexes
CREATE INDEX IF NOT EXISTS idx_caution_category ON ingredientcaution(category);
CREATE INDEX IF NOT EXISTS idx_caution_affected ON ingredientcaution(affected_characteristic);

-- Relationship Table Indexes
CREATE INDEX IF NOT EXISTS idx_snp_char_effect ON snp_characteristic_link(effect_direction, evidence_strength);
CREATE INDEX IF NOT EXISTS idx_snp_ing_evidence ON snp_ingredient_link(evidence_level, recommendation_strength);
CREATE INDEX IF NOT EXISTS idx_snp_caution_evidence ON snp_ingredientcaution_link(evidence_level);
CREATE INDEX IF NOT EXISTS idx_char_cond_relation ON characteristic_condition_link(relationship_type);
CREATE INDEX IF NOT EXISTS idx_cond_ing_recommendation ON condition_ingredient_link(recommendation_strength);

-- Full-text Search Indexes
CREATE INDEX IF NOT EXISTS idx_snp_effect_tsv ON snp USING GIN (effect_tsv);
CREATE INDEX IF NOT EXISTS idx_characteristic_description_tsv ON skincharacteristic USING GIN (description_tsv);
CREATE INDEX IF NOT EXISTS idx_ingredient_mechanism_tsv ON ingredient USING GIN (mechanism_tsv);

-- User Management Indexes
CREATE INDEX IF NOT EXISTS idx_user_dna_file_user ON user_dna_file(user_id);
CREATE INDEX IF NOT EXISTS idx_user_dna_file_hash ON user_dna_file(file_hash);
CREATE INDEX IF NOT EXISTS idx_user_analysis_user ON user_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analysis_created ON user_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_user_analysis_json ON user_analysis USING GIN (json_results);
CREATE INDEX IF NOT EXISTS idx_user_report_user ON user_report(user_id);
CREATE INDEX IF NOT EXISTS idx_user_report_created ON user_report(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(action_timestamp);

COMMIT;