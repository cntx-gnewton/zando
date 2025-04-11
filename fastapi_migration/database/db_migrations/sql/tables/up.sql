-- Create all tables with IF NOT EXISTS

--
-- Name: characteristic_condition_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.characteristic_condition_link (
    characteristic_id integer NOT NULL,
    condition_id integer NOT NULL,
    relationship_type character varying
);



--
-- Name: condition_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.condition_ingredient_link (
    condition_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    recommendation_strength character varying,
    guidance_notes text,
    CONSTRAINT condition_ingredient_link_recommendation_strength_check CHECK (((recommendation_strength)::text = ANY ((ARRAY['First-line'::character varying, 'Second-line'::character varying, 'Adjuvant'::character varying])::text[])))
);



--
-- Name: ingredient; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.ingredient (
    ingredient_id integer NOT NULL,
    name character varying NOT NULL,
    mechanism text,
    evidence_level character varying,
    contraindications text,
    CONSTRAINT ingredient_evidence_level_check CHECK (((evidence_level)::text = ANY ((ARRAY['Strong'::character varying, 'Moderate'::character varying, 'Weak'::character varying])::text[])))
);



--
-- Name: ingredientcaution; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.ingredientcaution (
    caution_id integer NOT NULL,
    ingredient_name character varying NOT NULL,
    category character varying NOT NULL,
    risk_mechanism text,
    affected_characteristic character varying,
    alternative_ingredients text
);



--
-- Name: skincondition; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.skincondition (
    condition_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    severity_scale text
);



--
-- Name: snp; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.snp (
    snp_id integer NOT NULL,
    rsid character varying NOT NULL,
    gene character varying NOT NULL,
    risk_allele character varying NOT NULL,
    effect text,
    evidence_strength character varying,
    category character varying NOT NULL,
    CONSTRAINT snp_evidence_strength_check CHECK (((evidence_strength)::text = ANY ((ARRAY['Strong'::character varying, 'Moderate'::character varying, 'Weak'::character varying])::text[])))
);



--
-- Name: snp_characteristic_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.snp_characteristic_link (
    snp_id integer NOT NULL,
    characteristic_id integer NOT NULL,
    effect_direction character varying,
    evidence_strength character varying,
    CONSTRAINT snp_characteristic_link_effect_direction_check CHECK (((effect_direction)::text = ANY ((ARRAY['Increases'::character varying, 'Decreases'::character varying, 'Modulates'::character varying])::text[])))
);



--
-- Name: snp_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.snp_ingredient_link (
    snp_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    benefit_mechanism text,
    recommendation_strength character varying,
    evidence_level character varying,
    CONSTRAINT snp_ingredient_link_evidence_level_check CHECK (((evidence_level)::text = ANY ((ARRAY['Strong'::character varying, 'Moderate'::character varying, 'Weak'::character varying])::text[]))),
    CONSTRAINT snp_ingredient_link_recommendation_strength_check CHECK (((recommendation_strength)::text = ANY ((ARRAY['First-line'::character varying, 'Second-line'::character varying, 'Supportive'::character varying])::text[])))
);



--
-- Name: snp_ingredientcaution_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.snp_ingredientcaution_link (
    snp_id integer NOT NULL,
    caution_id integer NOT NULL,
    evidence_level character varying,
    notes text,
    CONSTRAINT snp_ingredientcaution_link_evidence_level_check CHECK (((evidence_level)::text = ANY ((ARRAY['Strong'::character varying, 'Moderate'::character varying, 'Weak'::character varying])::text[])))
);



--
-- Name: product; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product (
    product_id integer NOT NULL,
    name character varying NOT NULL,
    brand character varying,
    type character varying,
    description text,
    directions text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);



--
-- Name: product_aspect; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_aspect (
    aspect_id integer NOT NULL,
    name character varying NOT NULL,
    category character varying,
    description text
);


--
-- Name: product_aspect_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_aspect_link (
    product_id integer NOT NULL,
    aspect_id integer NOT NULL
);



--
-- Name: product_benefit; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_benefit (
    benefit_id integer NOT NULL,
    name character varying NOT NULL,
    category character varying,
    description text
);



--
-- Name: product_benefit_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_benefit_link (
    product_id integer NOT NULL,
    benefit_id integer NOT NULL,
    strength character varying,
    CONSTRAINT product_benefit_link_strength_check CHECK (((strength)::text = ANY ((ARRAY['Primary'::character varying, 'Secondary'::character varying])::text[])))
);



--
-- Name: product_concern; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_concern (
    concern_id integer NOT NULL,
    name character varying NOT NULL,
    related_characteristic character varying,
    description text
);

--
-- Name: product_concern_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_concern_link (
    product_id integer NOT NULL,
    concern_id integer NOT NULL
);



--
-- Name: product_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_ingredient_link (
    product_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    is_active boolean DEFAULT false,
    concentration_percentage numeric
);


--
-- Name: product_routine_position; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_routine_position (
    position_id integer NOT NULL,
    product_id integer,
    routine_step public.routine_step_type NOT NULL,
    step_order integer
);



--
-- Name: product_genetic_suitability; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.product_genetic_suitability (
    product_id integer NOT NULL,
    snp_id integer NOT NULL,
    suitability_score integer,
    reason text,
    CONSTRAINT product_genetic_suitability_suitability_score_check CHECK (((suitability_score >= '-2'::integer) AND (suitability_score <= 2)))
);

--
-- Name: skincharacteristic; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.skincharacteristic (
    characteristic_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    measurement_method text
);




--
-- Name: report_log; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.report_log (
    log_id integer NOT NULL,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    report_summary text
);


--
-- Name: report_sections; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE IF NOT EXISTS public.report_sections (
    section_id integer NOT NULL,
    section_name character varying NOT NULL,
    display_order integer NOT NULL,
    section_type character varying NOT NULL,
    is_active boolean DEFAULT true
);