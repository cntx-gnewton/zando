-- Schema Enhancements for Zando Genomic Analysis
-- Migration 0003: Performance improvements and data integrity

BEGIN;

-- Performance Indexes
-- These indexes improve query performance for common access patterns

-- SNP Table Indexes (add compound indexes for common query patterns)
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

-- Full-text Search Capabilities
-- These will be used for searching text fields

-- Add full-text search for SNP effects
ALTER TABLE snp ADD COLUMN IF NOT EXISTS effect_tsv tsvector 
GENERATED ALWAYS AS (to_tsvector('english', coalesce(effect, ''))) STORED;
CREATE INDEX IF NOT EXISTS idx_snp_effect_tsv ON snp USING GIN (effect_tsv);

-- Add full-text search for characteristic descriptions
ALTER TABLE skincharacteristic ADD COLUMN IF NOT EXISTS description_tsv tsvector 
GENERATED ALWAYS AS (to_tsvector('english', coalesce(description, ''))) STORED;
CREATE INDEX IF NOT EXISTS idx_characteristic_description_tsv ON skincharacteristic USING GIN (description_tsv);

-- Add full-text search for ingredient mechanisms
ALTER TABLE ingredient ADD COLUMN IF NOT EXISTS mechanism_tsv tsvector 
GENERATED ALWAYS AS (to_tsvector('english', coalesce(mechanism, ''))) STORED;
CREATE INDEX IF NOT EXISTS idx_ingredient_mechanism_tsv ON ingredient USING GIN (mechanism_tsv);

-- User Management Tables
-- These tables support user authentication and profile management

-- Users Table
CREATE TABLE IF NOT EXISTS app_user (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

-- User DNA Files
CREATE TABLE IF NOT EXISTS user_dna_file (
    file_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(user_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    upload_date TIMESTAMP NOT NULL DEFAULT NOW(),
    file_size INTEGER NOT NULL,
    file_format VARCHAR(50),
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(50) DEFAULT 'pending',
    UNIQUE (user_id, file_hash)
);
CREATE INDEX IF NOT EXISTS idx_user_dna_file_user ON user_dna_file(user_id);
CREATE INDEX IF NOT EXISTS idx_user_dna_file_hash ON user_dna_file(file_hash);

-- User Analysis Results
CREATE TABLE IF NOT EXISTS user_analysis (
    analysis_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(user_id) ON DELETE CASCADE,
    file_id INTEGER REFERENCES user_dna_file(file_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    analysis_version VARCHAR(10) NOT NULL,
    total_snps_analyzed INTEGER NOT NULL,
    matching_snps INTEGER NOT NULL,
    summary TEXT,
    json_results JSONB,
    UNIQUE (user_id, file_id)
);
CREATE INDEX IF NOT EXISTS idx_user_analysis_user ON user_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analysis_created ON user_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_user_analysis_json ON user_analysis USING GIN (json_results);

-- User Generated Reports
CREATE TABLE IF NOT EXISTS user_report (
    report_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(user_id) ON DELETE CASCADE,
    analysis_id INTEGER REFERENCES user_analysis(analysis_id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    report_type VARCHAR(50) NOT NULL,
    report_version VARCHAR(10) NOT NULL,
    file_path VARCHAR(255),
    report_hash VARCHAR(64),
    is_generated BOOLEAN DEFAULT FALSE,
    UNIQUE (analysis_id, report_type)
);
CREATE INDEX IF NOT EXISTS idx_user_report_user ON user_report(user_id);
CREATE INDEX IF NOT EXISTS idx_user_report_created ON user_report(created_at);

-- Audit logs for security tracking
CREATE TABLE IF NOT EXISTS audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_user(user_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    action_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT,
    action_details JSONB
);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(action_timestamp);

-- User preferences for personalization
CREATE TABLE IF NOT EXISTS user_preference (
    user_id INTEGER REFERENCES app_user(user_id) ON DELETE CASCADE PRIMARY KEY,
    email_notifications BOOLEAN DEFAULT TRUE,
    dark_mode BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    preferences_json JSONB DEFAULT '{}'::jsonb
);

-- Foreign key constraints
-- Adding a few missing foreign key constraints for better data integrity
ALTER TABLE user_analysis
ADD CONSTRAINT fk_analysis_file
FOREIGN KEY (file_id) 
REFERENCES user_dna_file(file_id)
ON DELETE CASCADE;

ALTER TABLE user_report
ADD CONSTRAINT fk_report_analysis
FOREIGN KEY (analysis_id)
REFERENCES user_analysis(analysis_id)
ON DELETE CASCADE;

-- Add functions and triggers
-- To ensure data integrity and automatic timestamp updates

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update user_preference timestamps
DROP TRIGGER IF EXISTS update_user_preference_timestamp ON user_preference;
CREATE TRIGGER update_user_preference_timestamp
BEFORE UPDATE ON user_preference
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

COMMIT;