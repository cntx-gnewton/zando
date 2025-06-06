-- Clear existing data if needed
TRUNCATE TABLE skincharacteristic CASCADE;

-- Insert core skin characteristics
INSERT INTO skincharacteristic (name, description, measurement_method) VALUES
-- Pigmentation related
('Melanin Production', 'Ability to produce and distribute melanin pigment in response to UV exposure', 'Spectrophotometry and colorimetry measurements'),
('UV Sensitivity', 'Susceptibility to UV-induced damage and sunburn', 'Minimal Erythema Dose (MED) testing'),

-- Barrier function related
('Barrier Function', 'Skin''s ability to retain moisture and protect against environmental stressors', 'Trans-epidermal water loss (TEWL) measurements'),
('Hydration Level', 'Moisture content in the stratum corneum', 'Corneometry measurements'),

-- Inflammation related
('Inflammatory Response', 'Tendency to develop inflammatory reactions in the skin', 'Clinical assessment and biomarker analysis'),
('Immune Activity', 'Immune system activity in the skin', 'Cytokine level measurements'),

-- Structural characteristics
('Collagen Production', 'Rate of new collagen synthesis', 'Biopsy analysis and ultrasound measurement'),
('Elastin Quality', 'Skin elasticity and recoil capacity', 'Cutometry measurements'),

-- Protective mechanisms
('Antioxidant Capacity', 'Ability to neutralize free radicals and oxidative stress', 'Free radical testing and antioxidant assays'),
('DNA Repair Capacity', 'Efficiency of repairing UV-induced DNA damage', 'Comet assay and DNA damage markers'),

-- Vascular characteristics
('Vascular Reactivity', 'Blood vessel response to stimuli and tendency for flushing', 'Laser Doppler flowmetry'),
('Microcirculation', 'Quality of blood flow in small skin vessels', 'Capillary microscopy'),

-- Other key characteristics
('Sebum Production', 'Rate and quality of natural oil production', 'Sebumeter measurements'),
('Product Sensitivity', 'Tendency to react to skincare ingredients', 'Patch testing and reactivity assessment'),
('Circadian Rhythm Response', 'Skin''s daily biological rhythm patterns', 'Time-dependent barrier function measurements');

-- Verify the data
SELECT name, LEFT(description, 50) as short_description, measurement_method 
FROM skincharacteristic 
ORDER BY name;
