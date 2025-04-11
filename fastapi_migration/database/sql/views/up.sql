
--
-- Name: comprehensive_recommendations; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.comprehensive_recommendations AS
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
   FROM ((((((((public.snp s
     JOIN public.snp_characteristic_link scl ON ((s.snp_id = scl.snp_id)))
     JOIN public.characteristic_condition_link ccl ON ((scl.characteristic_id = ccl.characteristic_id)))
     JOIN public.skincondition sc ON ((ccl.condition_id = sc.condition_id)))
     JOIN public.condition_ingredient_link cil ON ((sc.condition_id = cil.condition_id)))
     JOIN public.ingredient i ON ((cil.ingredient_id = i.ingredient_id)))
     LEFT JOIN public.snp_ingredient_link sil ON (((s.snp_id = sil.snp_id) AND (i.ingredient_id = sil.ingredient_id))))
     LEFT JOIN public.snp_ingredientcaution_link sicl ON ((s.snp_id = sicl.snp_id)))
     LEFT JOIN public.ingredientcaution ic ON ((sicl.caution_id = ic.caution_id)));


--
-- Name: product_data_validation; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.product_data_validation AS
 SELECT p.product_id,
    p.name,
    p.brand,
    p.type,
    ( SELECT count(*) AS count
           FROM public.product_ingredient_link
          WHERE (product_ingredient_link.product_id = p.product_id)) AS ingredient_count,
    ( SELECT count(*) AS count
           FROM public.product_benefit_link
          WHERE (product_benefit_link.product_id = p.product_id)) AS benefit_count,
    ( SELECT count(*) AS count
           FROM public.product_aspect_link
          WHERE (product_aspect_link.product_id = p.product_id)) AS aspect_count,
    ( SELECT count(*) AS count
           FROM public.product_concern_link
          WHERE (product_concern_link.product_id = p.product_id)) AS concern_count,
        CASE
            WHEN (p.directions IS NULL) THEN 'Missing directions'::text
            WHEN (p.description IS NULL) THEN 'Missing description'::text
            ELSE 'Complete'::text
        END AS data_status
   FROM public.product p;



--
-- Name: product_details; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.product_details AS
 SELECT p.product_id,
    p.name,
    p.brand,
    p.type,
    p.description,
    array_agg(DISTINCT i.name) FILTER (WHERE (i.name IS NOT NULL)) AS ingredients,
    array_agg(DISTINCT pb.name) FILTER (WHERE (pb.name IS NOT NULL)) AS benefits,
    array_agg(DISTINCT pa.name) FILTER (WHERE (pa.name IS NOT NULL)) AS aspects,
    array_agg(DISTINCT pc.name) FILTER (WHERE (pc.name IS NOT NULL)) AS concerns,
    prp.routine_step
   FROM (((((((((public.product p
     LEFT JOIN public.product_ingredient_link pil ON ((p.product_id = pil.product_id)))
     LEFT JOIN public.ingredient i ON ((pil.ingredient_id = i.ingredient_id)))
     LEFT JOIN public.product_benefit_link pbl ON ((p.product_id = pbl.product_id)))
     LEFT JOIN public.product_benefit pb ON ((pbl.benefit_id = pb.benefit_id)))
     LEFT JOIN public.product_aspect_link pal ON ((p.product_id = pal.product_id)))
     LEFT JOIN public.product_aspect pa ON ((pal.aspect_id = pa.aspect_id)))
     LEFT JOIN public.product_concern_link pcl ON ((p.product_id = pcl.product_id)))
     LEFT JOIN public.product_concern pc ON ((pcl.concern_id = pc.concern_id)))
     LEFT JOIN public.product_routine_position prp ON ((p.product_id = prp.product_id)))
  GROUP BY p.product_id, p.name, p.brand, p.type, p.description, prp.routine_step;




--
-- Name: product_recommendation_summary; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.product_recommendation_summary AS
 SELECT p.name,
    p.brand,
    p.type,
    pc.total_score,
    pc.recommendation_level,
    string_agg(DISTINCT (i.name)::text, ', '::text) AS ingredients,
    string_agg(DISTINCT (pb.name)::text, ', '::text) AS benefits,
    pc.explanation
   FROM (((((public.product p
     CROSS JOIN LATERAL public.calculate_product_compatibility(p.product_id, ARRAY['rs61816761'::text, 'rs1805007'::text], '{"Barrier Function": true}'::jsonb, '{"needed_step": "Moisturizer"}'::jsonb) pc(total_score, ingredient_score, routine_score, characteristic_score, recommendation_level, key_benefits, cautions, explanation))
     LEFT JOIN public.product_ingredient_link pil ON ((p.product_id = pil.product_id)))
     LEFT JOIN public.ingredient i ON ((pil.ingredient_id = i.ingredient_id)))
     LEFT JOIN public.product_benefit_link pbl ON ((p.product_id = pbl.product_id)))
     LEFT JOIN public.product_benefit pb ON ((pbl.benefit_id = pb.benefit_id)))
  GROUP BY p.product_id, p.name, p.brand, p.type, pc.total_score, pc.recommendation_level, pc.explanation;



--
-- Name: product_recommendations; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.product_recommendations AS
 SELECT p.product_id,
    p.name,
    p.brand,
    p.type,
    pc.total_score,
    pc.recommendation_level,
    pc.key_benefits,
    pc.cautions,
    pc.explanation
   FROM public.product p,
    LATERAL public.calculate_product_compatibility(p.product_id, ARRAY[]::text[], '{}'::jsonb, '{}'::jsonb) pc(total_score, ingredient_score, routine_score, characteristic_score, recommendation_level, key_benefits, cautions, explanation)
  ORDER BY pc.total_score DESC;




--
-- Name: snp_beneficial_ingredients; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.snp_beneficial_ingredients AS
 SELECT s.rsid,
    s.gene,
    s.category AS genetic_category,
    i.name AS ingredient_name,
    i.mechanism AS ingredient_mechanism,
    sil.benefit_mechanism,
    sil.recommendation_strength,
    sil.evidence_level
   FROM ((public.snp_ingredient_link sil
     JOIN public.snp s ON ((s.snp_id = sil.snp_id)))
     JOIN public.ingredient i ON ((i.ingredient_id = sil.ingredient_id)))
  ORDER BY sil.evidence_level DESC, sil.recommendation_strength;



--
-- Name: snp_ingredient_cautions; Type: VIEW; Schema: public; Owner: cam
--

CREATE VIEW public.snp_ingredient_cautions AS
 SELECT s.rsid,
    s.gene,
    s.category AS genetic_category,
    s.evidence_strength AS genetic_evidence,
    ic.ingredient_name,
    ic.category AS caution_level,
    ic.risk_mechanism,
    ic.alternative_ingredients
   FROM ((public.snp_ingredientcaution_link scl
     JOIN public.snp s ON ((s.snp_id = scl.snp_id)))
     JOIN public.ingredientcaution ic ON ((ic.caution_id = scl.caution_id)));


