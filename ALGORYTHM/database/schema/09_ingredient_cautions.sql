-- Create new table for ingredients to avoid/watch
CREATE TABLE IF NOT EXISTS IngredientCaution (
    caution_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,  -- 'Avoid' or 'Use with Caution'
    risk_mechanism TEXT,
    affected_characteristic VARCHAR,
    alternative_ingredients TEXT
);

-- Populate with ingredients to avoid or use with caution
INSERT INTO IngredientCaution (ingredient_name, category, risk_mechanism, affected_characteristic, alternative_ingredients) VALUES
-- Retinoid Metabolism Issues (associated with ALDH3A2, CYP26A1 variants)
('Retinol', 'Use with Caution', 'May cause increased irritation in individuals with retinoid metabolism variants', 'Product Sensitivity', 'Bakuchiol, Peptides'),
('Tretinoin', 'Use with Caution', 'Higher risk of irritation in retinoid metabolism variant carriers', 'Product Sensitivity', 'Bakuchiol, Niacinamide'),

-- Barrier Function Issues (associated with FLG variants)
('Sodium Lauryl Sulfate', 'Avoid', 'Disrupts barrier function, particularly risky with FLG mutations', 'Barrier Function', 'Gentle sulfate-free cleansers'),
('Denatured Alcohol', 'Avoid', 'Can severely compromise impaired skin barrier', 'Barrier Function', 'Glycerin, Butylene Glycol'),
('Essential Oils', 'Use with Caution', 'May irritate sensitive or barrier-compromised skin', 'Barrier Function', 'Fragrance-free alternatives'),

-- Inflammation Risk (associated with IL6, TNF-α variants)
('High-concentration AHAs', 'Use with Caution', 'May trigger excessive inflammation in sensitive individuals', 'Inflammatory Response', 'PHAs, low concentration lactic acid'),
('Benzoyl Peroxide', 'Use with Caution', 'Can cause increased inflammation in sensitive skin', 'Inflammatory Response', 'Azelaic Acid, Niacinamide'),

-- Pigmentation Risk (associated with MC1R, TYR variants)
('Hydroquinone', 'Use with Caution', 'May cause paradoxical hyperpigmentation in some individuals', 'Melanin Production', 'Kojic Acid, Vitamin C, Arbutin'),
('Bergamot Oil', 'Avoid', 'Can cause photosensitivity and irregular pigmentation', 'UV Sensitivity', 'Photostable botanical extracts'),

-- Oxidative Stress Sensitivity (associated with SOD2, CAT variants)
('High-concentration Vitamin C', 'Use with Caution', 'May cause oxidative stress in sensitive individuals', 'Antioxidant Capacity', 'Lower concentrations, stable derivatives'),
('Unstable Antioxidants', 'Avoid', 'Can become pro-oxidant in certain conditions', 'Antioxidant Capacity', 'Stable antioxidant formulations'),

-- Vascular Reactivity (associated with NOS3 variants)
('Menthol', 'Use with Caution', 'Can trigger vasodilation and flushing', 'Vascular Reactivity', 'Centella Asiatica, Allantoin'),
('Peppermint Oil', 'Use with Caution', 'May increase facial flushing', 'Vascular Reactivity', 'Chamomile, Green Tea Extract'),

-- General Sensitivity (multiple genetic factors)
('Synthetic Fragrances', 'Use with Caution', 'Common trigger for sensitive skin reactions', 'Product Sensitivity', 'Fragrance-free formulations'),
('Chemical Sunscreen Filters', 'Use with Caution', 'May cause reactions in sensitive individuals', 'UV Sensitivity', 'Mineral sunscreens');

-- Create linking table for SNPs and ingredients to avoid
CREATE TABLE IF NOT EXISTS SNP_IngredientCaution_Link (
    snp_id INTEGER REFERENCES snp(snp_id),
    caution_id INTEGER REFERENCES IngredientCaution(caution_id),
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    notes TEXT,
    PRIMARY KEY (snp_id, caution_id)
);
