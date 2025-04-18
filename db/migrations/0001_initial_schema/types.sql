-- Custom Types for Zando Genomic Analysis

BEGIN;

-- Create custom type for genetic findings (used in report generation) if it doesn't exist
DO $$
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'genetic_finding') THEN
        CREATE TYPE genetic_finding AS (
            rsid text,
            gene text,
            category text,
            evidence_strength text,
            effect text,
            characteristics text[],
            beneficial_ingredients text[],
            caution_ingredients text[]
        );
    END IF;
END
$$;

-- Create custom type for PDF styling if it doesn't exist
DO $$
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pdf_style') THEN
        CREATE TYPE pdf_style AS (
            font_name text,
            font_size integer,
            alignment text,
            spacing numeric,
            is_bold boolean
        );
    END IF;
END
$$;

-- Create enum type for skincare routine steps if it doesn't exist
DO $$
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'routine_step_type') THEN
        CREATE TYPE routine_step_type AS ENUM (
            'Cleanser',
            'Treatment',
            'Moisturizer',
            'Sun Protection'
        );
    END IF;
END
$$;

COMMIT;