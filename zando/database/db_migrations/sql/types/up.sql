-- Drop types if they exist
DO $$
BEGIN
    DROP TYPE IF EXISTS public.genetic_finding CASCADE;
    DROP TYPE IF EXISTS public.pdf_style CASCADE;
    DROP TYPE IF EXISTS public.routine_step_type CASCADE;
END;
$$;

-- Create types with explicit schema qualification
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

-- Force visibility of the type with a sanity check
DO $$
BEGIN
    -- Verify type exists
    ASSERT (SELECT true FROM pg_type WHERE typname = 'genetic_finding'), 
           'Type genetic_finding was not created properly';
END;
$$;

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