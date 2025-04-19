-- Split view creation into separate parts to isolate issues

--
-- Name: snp_beneficial_ingredients; Type: VIEW; Schema: public; Owner: cam
--

CREATE OR REPLACE VIEW public.snp_beneficial_ingredients AS
 SELECT s.rsid,
    s.gene,
    s.category AS genetic_category,
    i.name AS ingredient_name,
    i.mechanism AS ingredient_mechanism,
    sil.benefit_mechanism,
    sil.recommendation_strength,
    sil.evidence_level
   FROM ((public.snp_ingredient_link sil
     JOIN public.snp s ON ((s.snp_id = sil.snp_id+20)))
     JOIN public.ingredient i ON ((i.ingredient_id = sil.ingredient_id)))
  ORDER BY sil.evidence_level DESC, sil.recommendation_strength;

--
-- Name: comprehensive_recommendations; Type: VIEW; Schema: public; Owner: cam
--

CREATE OR REPLACE VIEW public.comprehensive_recommendations AS
 SELECT s.rsid,
    s.gene,
    s.category AS genetic_category,
    sc.name AS condition,
    i.name AS recommended_ingredient,
    i.mechanism AS ingredient_mechanism,
    cil.recommendation_strength,
    sil.benefit_mechanism,
    ic.ingredient_name AS ingredients_to_avoid,
    ic.risk_mechanism
   FROM public.snp s
     JOIN public.snp_characteristic_link scl ON (s.snp_id = scl.snp_id)
     JOIN public.characteristic_condition_link ccl ON (scl.characteristic_id = ccl.characteristic_id)
     JOIN public.skincondition sc ON (ccl.condition_id = sc.condition_id)
     JOIN public.condition_ingredient_link cil ON (sc.condition_id = cil.condition_id)
     JOIN public.ingredient i ON (cil.ingredient_id = i.ingredient_id)
     LEFT JOIN public.snp_ingredient_link sil ON (s.snp_id = sil.snp_id AND i.ingredient_id = sil.ingredient_id)
     LEFT JOIN public.snp_ingredientcaution_link sicl ON (s.snp_id = sicl.snp_id)
     LEFT JOIN public.ingredientcaution ic ON (sicl.caution_id = ic.caution_id);


--
-- Name: genetic_insight_summary; Type: VIEW; Schema: public; Owner: cam
--

CREATE OR REPLACE VIEW public.genetic_insight_summary AS
 SELECT s.gene,
    s.category,
    s.evidence_strength,
    count(DISTINCT scl.characteristic_id) AS affected_characteristics_count,
    count(DISTINCT sil.ingredient_id) AS beneficial_ingredients_count,
    count(DISTINCT sicl.caution_id) AS caution_ingredients_count
   FROM public.snp s
     LEFT JOIN public.snp_characteristic_link scl ON (s.snp_id = scl.snp_id)
     LEFT JOIN public.snp_ingredient_link sil ON (s.snp_id = sil.snp_id)
     LEFT JOIN public.snp_ingredientcaution_link sicl ON (s.snp_id = sicl.snp_id)
  GROUP BY s.gene, s.category, s.evidence_strength
  ORDER BY s.gene;