-- Clear existing data if needed
TRUNCATE TABLE SkinCondition CASCADE;

-- Insert skin conditions
INSERT INTO SkinCondition (name, description, severity_scale) VALUES
-- Barrier-related conditions
('Eczema', 'Chronic inflammatory skin condition causing dry, itchy, and inflamed skin patches', 'EASI (Eczema Area and Severity Index)'),
('Dry Skin', 'Reduced skin moisture and barrier dysfunction leading to rough, flaky skin', 'Clinician-rated 0-4 scale'),

-- Pigmentation conditions
('Hyperpigmentation', 'Excess melanin production causing dark patches or spots', 'MASI (Melasma Area and Severity Index)'),
('Photosensitivity', 'Increased sensitivity to UV radiation leading to sunburns and damage', 'Fitzpatrick Scale'),

-- Inflammatory conditions
('Acne', 'Inflammatory condition affecting sebaceous glands and hair follicles', 'IGA (Investigator''s Global Assessment) Scale'),
('Rosacea', 'Chronic inflammatory condition causing facial redness and bumps', 'IGA-RSS (Rosacea Severity Score)'),
('Psoriasis', 'Autoimmune condition causing rapid skin cell turnover and inflammation', 'PASI (Psoriasis Area Severity Index)'),

-- Aging-related conditions
('Photoaging', 'Premature aging due to UV exposure and environmental damage', 'Glogau Photoaging Scale'),
('Loss of Elasticity', 'Reduced skin firmness and elasticity due to collagen/elastin changes', 'Cutometer measurements'),

-- Sensitivity conditions
('Contact Dermatitis', 'Skin inflammation caused by contact with irritants or allergens', 'CDSI (Contact Dermatitis Severity Index)'),
('Product Sensitivity', 'Increased reactivity to skincare ingredients and products', 'RSSS (Reactive Skin Severity Score)'),

-- Vascular conditions
('Telangiectasia', 'Visible dilated blood vessels near skin surface', 'Modified IGA for telangiectasia'),
('Facial Flushing', 'Temporary redness due to vasodilation', 'Clinician-rated 0-3 scale');

-- Verify the data
SELECT 
    name,
    LEFT(description, 50) as short_description,
    severity_scale
FROM SkinCondition 
ORDER BY name;
