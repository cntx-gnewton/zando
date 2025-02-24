-- Core tables
CREATE TABLE IF NOT EXISTS SNP (
    snp_id SERIAL PRIMARY KEY,
    rsid VARCHAR NOT NULL UNIQUE,
    gene VARCHAR NOT NULL,
    risk_allele VARCHAR NOT NULL,
    effect TEXT,
    evidence_strength VARCHAR CHECK (evidence_strength IN ('Strong', 'Moderate', 'Weak')),
    category VARCHAR NOT NULL
);

