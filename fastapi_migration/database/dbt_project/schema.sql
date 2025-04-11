-- Initial schema creation script for Zando database
-- This creates the raw tables that dbt will use as sources

BEGIN;

-- Custom Types
DO $$
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'genetic_finding') THEN
        CREATE TYPE genetic_finding AS (
            rsid text,
            gene text,
            category text,
            evidence_strength text,
            effect text,
            characteristics text[],
            beneficial_ingredients text[],
            caution_ingredients text[]
        );
    END IF;
END
$$;

DO $$
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pdf_style') THEN
        CREATE TYPE pdf_style AS (
            font_name text,
            font_size integer,
            alignment text,
            spacing numeric,
            is_bold boolean
        );
    END IF;
END
$$;

-- Create base tables
CREATE TABLE IF NOT EXISTS snp (
    snp_id SERIAL PRIMARY KEY,
    rsid VARCHAR(50) NOT NULL,
    gene VARCHAR(50) NOT NULL,
    risk_allele VARCHAR(10) NOT NULL,
    effect TEXT,
    evidence_strength VARCHAR(50),
    category VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS skincharacteristic (
    characteristic_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    measurement_method TEXT
);

CREATE TABLE IF NOT EXISTS skincondition (
    condition_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    severity_scale TEXT
);

CREATE TABLE IF NOT EXISTS ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    mechanism TEXT,
    evidence_level VARCHAR(50),
    contraindications TEXT
);

CREATE TABLE IF NOT EXISTS ingredientcaution (
    caution_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    risk_mechanism TEXT,
    affected_characteristic VARCHAR(100),
    alternative_ingredients TEXT
);

-- Create relationship tables
CREATE TABLE IF NOT EXISTS snp_characteristic_link (
    snp_id INTEGER REFERENCES snp(snp_id),
    characteristic_id INTEGER REFERENCES skincharacteristic(characteristic_id),
    effect_direction VARCHAR(50),
    evidence_strength VARCHAR(50),
    PRIMARY KEY (snp_id, characteristic_id)
);

CREATE TABLE IF NOT EXISTS characteristic_condition_link (
    characteristic_id INTEGER REFERENCES skincharacteristic(characteristic_id),
    condition_id INTEGER REFERENCES skincondition(condition_id),
    relationship_type VARCHAR(50),
    PRIMARY KEY (characteristic_id, condition_id)
);

CREATE TABLE IF NOT EXISTS condition_ingredient_link (
    condition_id INTEGER REFERENCES skincondition(condition_id),
    ingredient_id INTEGER REFERENCES ingredient(ingredient_id),
    recommendation_strength VARCHAR(50),
    guidance_notes TEXT,
    PRIMARY KEY (condition_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS snp_ingredient_link (
    snp_id INTEGER REFERENCES snp(snp_id),
    ingredient_id INTEGER REFERENCES ingredient(ingredient_id),
    benefit_mechanism TEXT,
    recommendation_strength VARCHAR(50),
    evidence_level VARCHAR(50),
    PRIMARY KEY (snp_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS snp_ingredientcaution_link (
    snp_id INTEGER REFERENCES snp(snp_id),
    caution_id INTEGER REFERENCES ingredientcaution(caution_id),
    evidence_level VARCHAR(50),
    notes TEXT,
    PRIMARY KEY (snp_id, caution_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_snp_rsid ON snp(rsid);
CREATE INDEX IF NOT EXISTS idx_snp_gene ON snp(gene);
CREATE INDEX IF NOT EXISTS idx_characteristic_name ON skincharacteristic(name);
CREATE INDEX IF NOT EXISTS idx_condition_name ON skincondition(name);
CREATE INDEX IF NOT EXISTS idx_ingredient_name ON ingredient(name);
CREATE INDEX IF NOT EXISTS idx_caution_ingredient_name ON ingredientcaution(ingredient_name);

COMMIT;