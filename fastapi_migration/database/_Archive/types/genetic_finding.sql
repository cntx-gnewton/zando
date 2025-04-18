
-- Drop the type if it exists
DROP TYPE IF EXISTS genetic_finding CASCADE;

-- Create the genetic_finding type
CREATE TYPE public.genetic_finding AS (
	rsid text,
	gene text,
	category text,
	evidence_strength text,
	effect text,
	characteristics text[],
	beneficial_ingredients text[],
	caution_ingredients text[]
);



-- Function to convert TEXT to genetic_finding
CREATE OR REPLACE FUNCTION text_to_genetic_finding(input TEXT)
RETURNS genetic_finding AS $$
DECLARE
    result genetic_finding;
BEGIN
    -- Assuming the input text is in a specific format, e.g., JSON
    SELECT
        (json_populate_record(NULL::genetic_finding, input::json)).*
    INTO
        result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


-- Create a cast for the genetic_finding type
CREATE CAST (TEXT AS genetic_finding) WITH FUNCTION text_to_genetic_finding(TEXT) AS IMPLICIT;