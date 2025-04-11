-- Database Functions for Zando Genomic Analysis
-- Migration 0004: Adding PostgreSQL functions for common operations

BEGIN;

-- This migration is split into multiple files for maintainability.
-- Each file contains a specific category of functions.

-- The files should be processed in order:
-- 1. Extensions
-- 2. Utility Functions
-- 3. Search Functions
-- 4. Analysis Functions
-- 5. Reporting Functions
-- 6. Analysis Summary Function
-- 7. User Management Functions

-- Function implementations are contained in the functions/ directory
-- and will be loaded by the migration script.

COMMIT;