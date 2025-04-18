--
-- Name: product_data_validation; Type: VIEW; Schema: public; Owner: cam
--

CREATE OR REPLACE VIEW public.product_data_validation AS
 SELECT p.product_id,
    p.name AS product_name,
    p.brand,
    p.type,
    string_agg(DISTINCT i.name, ', '::text) AS active_ingredients,
    string_agg(DISTINCT pb.name, ', '::text) AS benefits,
    string_agg(DISTINCT a.name, ', '::text) AS aspects,
    string_agg(DISTINCT c.name, ', '::text) AS addressed_concerns
   FROM public.product p
     LEFT JOIN public.product_ingredient_link pil ON (p.product_id = pil.product_id)
     LEFT JOIN public.ingredient i ON (pil.ingredient_id = i.ingredient_id AND pil.is_active)
     LEFT JOIN public.product_benefit_link pbl ON (p.product_id = pbl.product_id)
     LEFT JOIN public.product_benefit pb ON (pbl.benefit_id = pb.benefit_id)
     LEFT JOIN public.product_aspect_link pal ON (p.product_id = pal.product_id)
     LEFT JOIN public.product_aspect a ON (pal.aspect_id = a.aspect_id)
     LEFT JOIN public.product_concern_link pcl ON (p.product_id = pcl.product_id)
     LEFT JOIN public.product_concern c ON (pcl.concern_id = c.concern_id)
  GROUP BY p.product_id, p.name, p.brand, p.type
  ORDER BY p.brand, p.name;