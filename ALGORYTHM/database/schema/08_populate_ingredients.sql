-- Clear existing data if needed
TRUNCATE TABLE Ingredient CASCADE;

-- Insert ingredients
INSERT INTO Ingredient (name, mechanism, evidence_level, contraindications) VALUES
-- Barrier Function & Hydration
('Ceramides', 'Restore and strengthen skin barrier function by replacing natural lipids', 'Strong', 'None known'),
('Hyaluronic Acid', 'Hydrates by binding water molecules in the skin', 'Strong', 'None significant'),
('Niacinamide', 'Supports barrier function, reduces inflammation, regulates sebum', 'Strong', 'Rare flushing in sensitive individuals'),
('Squalane', 'Emollient that mimics skin''s natural oils', 'Moderate', 'None known'),

-- Antioxidants & Protection
('Vitamin C (L-Ascorbic Acid)', 'Antioxidant, collagen synthesis support, brightening', 'Strong', 'Can be irritating at high concentrations'),
('Vitamin E (Tocopherol)', 'Antioxidant, moisturizing, strengthens skin barrier', 'Strong', 'May cause contact dermatitis in some'),
('Green Tea Extract', 'Antioxidant, anti-inflammatory, photoprotective', 'Moderate', 'None significant'),
('Resveratrol', 'Antioxidant, anti-aging, protects against UV damage', 'Moderate', 'May increase sensitivity to retinoids'),

-- Cell Turnover & Anti-aging
('Retinoids', 'Increase cell turnover, stimulate collagen, reduce pigmentation', 'Strong', 'Pregnancy, sun sensitivity, initial irritation'),
('Peptides', 'Signal collagen production, improve skin firmness', 'Moderate', 'None significant'),
('Glycolic Acid', 'Exfoliates, improves texture, stimulates collagen', 'Strong', 'Sun sensitivity, may irritate sensitive skin'),
('Lactic Acid', 'Gentle exfoliation, hydration, improves texture', 'Strong', 'May cause temporary sensitivity'),

-- Pigmentation
('Kojic Acid', 'Inhibits tyrosinase, reduces melanin production', 'Moderate', 'May cause skin irritation'),
('Vitamin B12', 'Reduces hyperpigmentation, supports cell renewal', 'Moderate', 'None significant'),
('Arbutin', 'Natural tyrosinase inhibitor, reduces pigmentation', 'Strong', 'None significant'),
('Tranexamic Acid', 'Reduces melanin production and inflammation', 'Strong', 'Rare allergic reactions'),

-- Anti-inflammatory
('Centella Asiatica', 'Calms inflammation, supports healing', 'Strong', 'Rare allergic reactions'),
('Zinc Oxide', 'Soothes skin, provides UV protection', 'Strong', 'None significant'),
('Colloidal Oatmeal', 'Reduces inflammation, supports barrier function', 'Strong', 'Rare cereal allergies'),
('Aloe Vera', 'Soothes inflammation, provides hydration', 'Moderate', 'Rare allergic reactions'),

-- Specialized Actives
('Azelaic Acid', 'Anti-inflammatory, reduces pigmentation and acne', 'Strong', 'Initial tingling sensation'),
('Bakuchiol', 'Natural retinol alternative, gentler cell turnover', 'Moderate', 'None significant'),
('Polyglutamic Acid', 'Superior hydration, supports barrier function', 'Moderate', 'None known'),
('Beta Glucan', 'Soothes, strengthens barrier, supports healing', 'Moderate', 'None significant');

-- Verify the data
SELECT 
    name,
    evidence_level,
    LEFT(mechanism, 50) as short_mechanism,
    contraindications
FROM Ingredient 
ORDER BY evidence_level DESC, name;
