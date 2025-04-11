-- Initial Database Schema for Zando Genomic Analysis
-- This file creates the core tables for the application

BEGIN;

-- Create SNP table
CREATE TABLE IF NOT EXISTS SNP (
    snp_id SERIAL PRIMARY KEY,
    rsid VARCHAR NOT NULL UNIQUE,
    gene VARCHAR NOT NULL,
    risk_allele VARCHAR NOT NULL,
    effect TEXT,
    evidence_strength VARCHAR CHECK (evidence_strength IN ('Strong', 'Moderate', 'Weak')),
    category VARCHAR NOT NULL
);

-- Create SkinCharacteristic table
CREATE TABLE IF NOT EXISTS SkinCharacteristic (
    characteristic_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    measurement_method TEXT
);

-- Create SkinCondition table
CREATE TABLE IF NOT EXISTS SkinCondition (
    condition_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    severity_scale TEXT
);

-- Create Ingredient table
CREATE TABLE IF NOT EXISTS Ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    mechanism TEXT,
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    contraindications TEXT
);

-- Create IngredientCaution table
CREATE TABLE IF NOT EXISTS IngredientCaution (
    caution_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    risk_mechanism TEXT,
    affected_characteristic VARCHAR,
    alternative_ingredients TEXT
);

-- Create relationship/junction tables
CREATE TABLE IF NOT EXISTS SNP_Characteristic_Link (
    snp_id INTEGER REFERENCES snp(snp_id) ON DELETE CASCADE,
    characteristic_id INTEGER REFERENCES SkinCharacteristic(characteristic_id) ON DELETE CASCADE,
    effect_direction VARCHAR CHECK (effect_direction IN ('Increases', 'Decreases', 'Modulates')),
    evidence_strength VARCHAR,
    PRIMARY KEY (snp_id, characteristic_id)
);

CREATE TABLE IF NOT EXISTS Characteristic_Condition_Link (
    characteristic_id INTEGER REFERENCES SkinCharacteristic(characteristic_id) ON DELETE CASCADE,
    condition_id INTEGER REFERENCES SkinCondition(condition_id) ON DELETE CASCADE,
    relationship_type VARCHAR,
    PRIMARY KEY (characteristic_id, condition_id)
);

CREATE TABLE IF NOT EXISTS SNP_Ingredient_Link (
    snp_id INTEGER REFERENCES snp(snp_id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES Ingredient(ingredient_id) ON DELETE CASCADE,
    benefit_mechanism TEXT,
    recommendation_strength VARCHAR CHECK (recommendation_strength IN ('First-line', 'Second-line', 'Supportive')),
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    PRIMARY KEY (snp_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS SNP_IngredientCaution_Link (
    snp_id INTEGER REFERENCES snp(snp_id) ON DELETE CASCADE,
    caution_id INTEGER REFERENCES IngredientCaution(caution_id) ON DELETE CASCADE,
    relationship_notes TEXT,
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    PRIMARY KEY (snp_id, caution_id)
);

CREATE TABLE IF NOT EXISTS Condition_Ingredient_Link (
    condition_id INTEGER REFERENCES SkinCondition(condition_id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES Ingredient(ingredient_id) ON DELETE CASCADE,
    recommendation_strength VARCHAR CHECK (recommendation_strength IN ('First-line', 'Second-line', 'Adjuvant')),
    guidance_notes TEXT,
    PRIMARY KEY (condition_id, ingredient_id)
);

-- Basic indexes for commonly queried columns
CREATE INDEX IF NOT EXISTS idx_snp_rsid ON snp(rsid);
CREATE INDEX IF NOT EXISTS idx_snp_gene ON snp(gene);
CREATE INDEX IF NOT EXISTS idx_snp_category ON snp(category);

CREATE INDEX IF NOT EXISTS idx_characteristic_name ON skincharacteristic(name);
CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredient(name);
CREATE INDEX IF NOT EXISTS idx_ingredientcaution_name ON ingredientcaution(ingredient_name);

COMMIT;