-- Drop types if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'genetic_finding') THEN
        DROP TYPE public.genetic_finding CASCADE;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'pdf_style') THEN
        DROP TYPE public.pdf_style CASCADE;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'routine_step_type') THEN
        DROP TYPE public.routine_step_type CASCADE;
    END IF;
END
$$;

-- Create types
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

--
-- Name: pdf_style; Type: TYPE; Schema: public; Owner: cam
--

CREATE TYPE public.pdf_style AS (
	font_name text,
	font_size integer,
	alignment text,
	spacing numeric,
	is_bold boolean
);

--
-- Name: routine_step_type; Type: TYPE; Schema: public; Owner: cam
--

CREATE TYPE public.routine_step_type AS ENUM (
    'Cleanser',
    'Treatment',
    'Moisturizer',
    'Sun Protection'
);