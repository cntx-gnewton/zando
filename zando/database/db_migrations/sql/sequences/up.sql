-- Create sequences if they don't exist

--
-- Name: ingredient_ingredient_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.ingredient_ingredient_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: ingredient_ingredient_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.ingredient_ingredient_id_seq OWNED BY public.ingredient.ingredient_id;


--
-- Name: ingredientcaution_caution_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.ingredientcaution_caution_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: ingredientcaution_caution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.ingredientcaution_caution_id_seq OWNED BY public.ingredientcaution.caution_id;



--
-- Name: product_aspect_aspect_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.product_aspect_aspect_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_aspect_aspect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.product_aspect_aspect_id_seq OWNED BY public.product_aspect.aspect_id;



--
-- Name: product_benefit_benefit_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.product_benefit_benefit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_benefit_benefit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.product_benefit_benefit_id_seq OWNED BY public.product_benefit.benefit_id;

--
-- Name: product_concern_concern_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.product_concern_concern_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_concern_concern_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.product_concern_concern_id_seq OWNED BY public.product_concern.concern_id;


--
-- Name: product_product_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.product_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.product_product_id_seq OWNED BY public.product.product_id;


--
-- Name: product_routine_position_position_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.product_routine_position_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_routine_position_position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.product_routine_position_position_id_seq OWNED BY public.product_routine_position.position_id;



--
-- Name: report_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.report_log_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: report_log_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.report_log_log_id_seq OWNED BY public.report_log.log_id;



--
-- Name: report_sections_section_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.report_sections_section_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: report_sections_section_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.report_sections_section_id_seq OWNED BY public.report_sections.section_id;


--
-- Name: skincharacteristic_characteristic_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.skincharacteristic_characteristic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: skincharacteristic_characteristic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.skincharacteristic_characteristic_id_seq OWNED BY public.skincharacteristic.characteristic_id;


--
-- Name: skincondition_condition_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.skincondition_condition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: skincondition_condition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.skincondition_condition_id_seq OWNED BY public.skincondition.condition_id;


--
-- Name: snp_snp_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE IF NOT EXISTS public.snp_snp_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: snp_snp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cam
--

ALTER SEQUENCE public.snp_snp_id_seq OWNED BY public.snp.snp_id;



--
-- Name: ingredient ingredient_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.ingredient ALTER COLUMN ingredient_id SET DEFAULT nextval('public.ingredient_ingredient_id_seq'::regclass);


--
-- Name: ingredientcaution caution_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.ingredientcaution ALTER COLUMN caution_id SET DEFAULT nextval('public.ingredientcaution_caution_id_seq'::regclass);


--
-- Name: product product_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.product ALTER COLUMN product_id SET DEFAULT nextval('public.product_product_id_seq'::regclass);


--
-- Name: product_aspect aspect_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.product_aspect ALTER COLUMN aspect_id SET DEFAULT nextval('public.product_aspect_aspect_id_seq'::regclass);


--
-- Name: product_benefit benefit_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.product_benefit ALTER COLUMN benefit_id SET DEFAULT nextval('public.product_benefit_benefit_id_seq'::regclass);


--
-- Name: product_concern concern_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.product_concern ALTER COLUMN concern_id SET DEFAULT nextval('public.product_concern_concern_id_seq'::regclass);


--
-- Name: product_routine_position position_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.product_routine_position ALTER COLUMN position_id SET DEFAULT nextval('public.product_routine_position_position_id_seq'::regclass);


--
-- Name: report_log log_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.report_log ALTER COLUMN log_id SET DEFAULT nextval('public.report_log_log_id_seq'::regclass);


--
-- Name: report_sections section_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.report_sections ALTER COLUMN section_id SET DEFAULT nextval('public.report_sections_section_id_seq'::regclass);


--
-- Name: skincharacteristic characteristic_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.skincharacteristic ALTER COLUMN characteristic_id SET DEFAULT nextval('public.skincharacteristic_characteristic_id_seq'::regclass);


--
-- Name: skincondition condition_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.skincondition ALTER COLUMN condition_id SET DEFAULT nextval('public.skincondition_condition_id_seq'::regclass);


--
-- Name: snp snp_id; Type: DEFAULT; Schema: public; Owner: cam
--

ALTER TABLE ONLY public.snp ALTER COLUMN snp_id SET DEFAULT nextval('public.snp_snp_id_seq'::regclass);
