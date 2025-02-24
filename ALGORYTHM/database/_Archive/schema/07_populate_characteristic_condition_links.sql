-- Clear existing data if needed
TRUNCATE TABLE Characteristic_Condition_Link;

-- Insert Characteristic-Condition relationships
INSERT INTO Characteristic_Condition_Link (characteristic_id, condition_id, relationship_type)
SELECT c.characteristic_id, sc.condition_id, 'Primary'
FROM skincharacteristic c, skincondition sc
WHERE 
    -- Barrier Function relationships
    (c.name = 'Barrier Function' AND sc.name IN ('Eczema', 'Dry Skin', 'Contact Dermatitis'))
    OR
    -- Hydration Level relationships
    (c.name = 'Hydration Level' AND sc.name IN ('Dry Skin', 'Eczema'))
    OR
    -- Melanin Production relationships
    (c.name = 'Melanin Production' AND sc.name IN ('Hyperpigmentation', 'Photosensitivity'))
    OR
    -- UV Sensitivity relationships
    (c.name = 'UV Sensitivity' AND sc.name IN ('Photosensitivity', 'Photoaging'))
    OR
    -- Inflammatory Response relationships
    (c.name = 'Inflammatory Response' AND sc.name IN ('Acne', 'Rosacea', 'Psoriasis', 'Contact Dermatitis'))
    OR
    -- Immune Activity relationships
    (c.name = 'Immune Activity' AND sc.name IN ('Psoriasis', 'Contact Dermatitis'))
    OR
    -- Collagen Production relationships
    (c.name = 'Collagen Production' AND sc.name IN ('Photoaging', 'Loss of Elasticity'))
    OR
    -- Elastin Quality relationships
    (c.name = 'Elastin Quality' AND sc.name = 'Loss of Elasticity')
    OR
    -- Antioxidant Capacity relationships
    (c.name = 'Antioxidant Capacity' AND sc.name IN ('Photoaging', 'Photosensitivity'))
    OR
    -- Vascular Reactivity relationships
    (c.name = 'Vascular Reactivity' AND sc.name IN ('Facial Flushing', 'Telangiectasia', 'Rosacea'))
    OR
    -- Microcirculation relationships
    (c.name = 'Microcirculation' AND sc.name IN ('Telangiectasia', 'Facial Flushing'))
    OR
    -- Product Sensitivity relationships
    (c.name = 'Product Sensitivity' AND sc.name IN ('Contact Dermatitis', 'Product Sensitivity'));

-- Add secondary relationships
INSERT INTO Characteristic_Condition_Link (characteristic_id, condition_id, relationship_type)
SELECT c.characteristic_id, sc.condition_id, 'Secondary'
FROM skincharacteristic c, skincondition sc
WHERE 
    -- Secondary relationships for Inflammatory Response
    (c.name = 'Inflammatory Response' AND sc.name IN ('Hyperpigmentation', 'Loss of Elasticity'))
    OR
    -- Secondary relationships for Barrier Function
    (c.name = 'Barrier Function' AND sc.name IN ('Acne', 'Rosacea'))
    OR
    -- Secondary relationships for Antioxidant Capacity
    (c.name = 'Antioxidant Capacity' AND sc.name IN ('Loss of Elasticity', 'Hyperpigmentation'));

-- Verify the relationships
SELECT 
    c.name as characteristic,
    sc.name as condition,
    ccl.relationship_type
FROM Characteristic_Condition_Link ccl
JOIN skincharacteristic c ON c.characteristic_id = ccl.characteristic_id
JOIN skincondition sc ON sc.condition_id = ccl.condition_id
ORDER BY ccl.relationship_type, c.name, sc.name;
