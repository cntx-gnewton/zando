-- Rollback for data population
BEGIN;

-- Clear data from tables
TRUNCATE TABLE snp CASCADE;
TRUNCATE TABLE skincharacteristic CASCADE;

COMMIT;