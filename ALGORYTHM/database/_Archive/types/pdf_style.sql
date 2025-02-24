-- Drop the type if it exists
DROP TYPE IF EXISTS public.pdf_style CASCADE;

CREATE TYPE public.pdf_style AS (
	font_name text,
	font_size integer,
	alignment text,
	spacing numeric,
	is_bold boolean
);