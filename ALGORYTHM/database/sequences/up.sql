
--
-- Name: ingredient_ingredient_id_seq; Type: SEQUENCE; Schema: public; Owner: cam
--

CREATE SEQUENCE public.ingredient_ingredient_id_seq
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

CREATE SEQUENCE public.ingredientcaution_caution_id_seq
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

CREATE SEQUENCE public.product_aspect_aspect_id_seq
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

CREATE SEQUENCE public.product_benefit_benefit_id_seq
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

CREATE SEQUENCE public.product_concern_concern_id_seq
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

CREATE SEQUENCE public.product_product_id_seq
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

CREATE SEQUENCE public.product_routine_position_position_id_seq
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

CREATE SEQUENCE public.report_log_log_id_seq
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

CREATE SEQUENCE public.report_sections_section_id_seq
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

CREATE SEQUENCE public.skincharacteristic_characteristic_id_seq
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

CREATE SEQUENCE public.skincondition_condition_id_seq
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

CREATE SEQUENCE public.snp_snp_id_seq
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

