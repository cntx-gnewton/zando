-- Populate core tables with data from CSV files
BEGIN;

-- Clear existing data to ensure idempotence
TRUNCATE TABLE snp CASCADE;
TRUNCATE TABLE skincharacteristic CASCADE;
TRUNCATE TABLE ingredient CASCADE;
TRUNCATE TABLE ingredientcaution CASCADE;
TRUNCATE TABLE skincondition CASCADE;
TRUNCATE TABLE snp_characteristic_link CASCADE;
TRUNCATE TABLE snp_ingredient_link CASCADE;
TRUNCATE TABLE snp_ingredientcaution_link CASCADE;
TRUNCATE TABLE characteristic_condition_link CASCADE;
TRUNCATE TABLE condition_ingredient_link CASCADE;

-- We don't use \COPY because it doesn't work well with remote databases
-- Instead, the migration script will handle the data loading

-- Verify the loaded data
SELECT COUNT(*) AS snp_count FROM snp;
SELECT COUNT(*) AS characteristic_count FROM skincharacteristic;
SELECT COUNT(*) AS ingredient_count FROM ingredient;
SELECT COUNT(*) AS caution_count FROM ingredientcaution;
SELECT COUNT(*) AS condition_count FROM skincondition;

COMMIT;