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
