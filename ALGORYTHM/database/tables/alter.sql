
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
