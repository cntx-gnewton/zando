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

-- Create linking tables
CREATE TABLE IF NOT EXISTS SNP_Characteristic_Link (
    snp_id INTEGER REFERENCES snp(snp_id),
    characteristic_id INTEGER REFERENCES SkinCharacteristic(characteristic_id),
    effect_direction VARCHAR CHECK (effect_direction IN ('Increases', 'Decreases', 'Modulates')),
    evidence_strength VARCHAR,
    PRIMARY KEY (snp_id, characteristic_id)
);

CREATE TABLE IF NOT EXISTS Characteristic_Condition_Link (
    characteristic_id INTEGER REFERENCES SkinCharacteristic(characteristic_id),
    condition_id INTEGER REFERENCES SkinCondition(condition_id),
    relationship_type VARCHAR,
    PRIMARY KEY (characteristic_id, condition_id)
);

CREATE TABLE IF NOT EXISTS Condition_Ingredient_Link (
    condition_id INTEGER REFERENCES SkinCondition(condition_id),
    ingredient_id INTEGER REFERENCES Ingredient(ingredient_id),
    recommendation_strength VARCHAR CHECK (recommendation_strength IN ('First-line', 'Second-line', 'Adjuvant')),
    guidance_notes TEXT,
    PRIMARY KEY (condition_id, ingredient_id)
);
