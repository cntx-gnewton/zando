--
-- Name: analyze_genetic_risks(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.analyze_genetic_risks(user_rsids text[]) RETURNS TABLE(gene text, category text, evidence_strength text, affected_characteristics text[], risk_level text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.gene::text,
        s.category::text,
        s.evidence_strength::text,
        ARRAY_AGG(DISTINCT sc.name::text),
        (CASE
            WHEN s.evidence_strength = 'Strong' THEN 'High'
            WHEN s.evidence_strength = 'Moderate' THEN 'Medium'
            ELSE 'Low'
        END)::text as risk_level
    FROM snp s
    JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    WHERE s.rsid = ANY(user_rsids)
    GROUP BY s.gene, s.category, s.evidence_strength;
END;
$$;


--
-- Name: find_beneficial_ingredients(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.find_beneficial_ingredients(user_rsids text[]) RETURNS TABLE(gene text, ingredient_name text, benefit_mechanism text, recommendation_strength text, evidence_level text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        s.gene::text,
        i.name::text,
        sil.benefit_mechanism::text,
        sil.recommendation_strength::text,
        sil.evidence_level::text
    FROM snp s
    JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
    JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
    WHERE s.rsid = ANY(user_rsids)
    ORDER BY 
        CASE
            WHEN sil.recommendation_strength = 'First-line' THEN 1
            WHEN sil.recommendation_strength = 'Second-line' THEN 2
            ELSE 3
        END,
        CASE 
            WHEN sil.evidence_level = 'Strong' THEN 1
            WHEN sil.evidence_level = 'Moderate' THEN 2
            ELSE 3
        END;
END;
$$;


--
-- Name: find_genetic_characteristics(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.find_genetic_characteristics(user_rsids text[]) RETURNS TABLE(characteristic_name text, effect_direction text, gene text, category text, affected_conditions text[])
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sc.name::text,
        scl.effect_direction::text,
        s.gene::text,
        s.category::text,
        ARRAY_AGG(DISTINCT cond.name::text)
    FROM snp s
    JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    LEFT JOIN characteristic_condition_link ccl ON sc.characteristic_id = ccl.characteristic_id
    LEFT JOIN skincondition cond ON ccl.condition_id = cond.condition_id
    WHERE s.rsid = ANY(user_rsids)
    GROUP BY sc.name, scl.effect_direction, s.gene, s.category
    ORDER BY s.gene;
END;
$$;


--
-- Name: find_ingredient_cautions(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.find_ingredient_cautions(user_rsids text[]) RETURNS TABLE(gene text, ingredient_name text, category text, risk_mechanism text, evidence_level text, affected_characteristic text, alternative_ingredients text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        s.gene::text,
        ic.ingredient_name::text,
        ic.category::text,
        ic.risk_mechanism::text,
        sicl.evidence_level::text,
        ic.affected_characteristic::text,
        ic.alternative_ingredients::text
    FROM snp s
    JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
    JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    WHERE s.rsid = ANY(user_rsids)
    ORDER BY 
        CASE 
            WHEN sicl.evidence_level = 'Strong' THEN 1
            WHEN sicl.evidence_level = 'Moderate' THEN 2
            ELSE 3
        END;
END;
$$;


--
-- Name: format_pdf_section(text, text[], public.pdf_style); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.format_pdf_section(section_title text, content_items text[], style public.pdf_style) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    formatted_text text;
    style_tag text;
BEGIN
    -- Generate basic styling tags based on the provided style
    style_tag := '<style font="' || style.font_name || '" size="' || style.font_size || '"';
    
    IF style.is_bold THEN
        style_tag := style_tag || ' bold="true"';
    END IF;
    
    style_tag := style_tag || ' alignment="' || style.alignment || '">';
    
    -- Format the section title
    formatted_text := style_tag || '<b>' || section_title || '</b></style><br/>';
    
    -- Format each content item
    FOR i IN 1..array_length(content_items, 1) LOOP
        formatted_text := formatted_text || style_tag || content_items[i] || '</style><br/>';
        
        -- Add spacing between items
        IF i < array_length(content_items, 1) THEN
            formatted_text := formatted_text || '<spacer height="' || style.spacing || '"/>';
        END IF;
    END LOOP;
    
    RETURN formatted_text;
END;
$$;


--
-- Name: generate_characteristic_section(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE OR REPLACE FUNCTION public.generate_characteristic_section(user_rsids text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    result_text text := '';
    char_record record;
BEGIN
    FOR char_record IN (
        SELECT 
            sc.name as characteristic,
            scl.effect_direction,
            string_agg(distinct s.gene, ', ') as genes,
            string_agg(distinct cond.name, ', ') as conditions
        FROM snp s
        JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
        JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
        LEFT JOIN characteristic_condition_link ccl ON sc.characteristic_id = ccl.characteristic_id
        LEFT JOIN skincondition cond ON ccl.condition_id = cond.condition_id
        WHERE s.rsid = ANY(user_rsids)
        GROUP BY sc.name, scl.effect_direction
        ORDER BY sc.name
    ) LOOP
        result_text := result_text || '<characteristic>';
        result_text := result_text || '<name>' || char_record.characteristic || '</name>';
        result_text := result_text || '<effect>' || char_record.effect_direction || '</effect>';
        result_text := result_text || '<genes>' || char_record.genes || '</genes>';
        
        IF char_record.conditions IS NOT NULL THEN
            result_text := result_text || '<related_conditions>' || char_record.conditions || '</related_conditions>';
        END IF;
        
        result_text := result_text || '</characteristic>';
    END LOOP;
    
    RETURN '<characteristics>' || result_text || '</characteristics>';
END;
$$;
--
-- DO $$
-- BEGIN
--     DROP TYPE IF EXISTS public.genetic_finding CASCADE;
-- END;
-- $$;
-- CREATE TYPE public.genetic_finding AS (
-- 	rsid text,
-- 	gene text,
-- 	category text,
-- 	evidence_strength text,
-- 	effect text,
-- 	characteristics text[],
-- 	beneficial_ingredients text[],
-- 	caution_ingredients text[]
-- );


--
-- Name: generate_genetic_analysis_section(text[]); Type: FUNCTION; Schema: public; Owner: cam
--
-- --OLD VERSION--
-- CREATE OR REPLACE FUNCTION public.generate_genetic_analysis_section(user_rsids text[]) RETURNS text
--     LANGUAGE plpgsql
--     AS $$
-- DECLARE
--     result_text text := '';
--     gene_record record;
-- BEGIN
--     FOR gene_record IN (
--         SELECT
--             s.gene,
--             s.category,
--             s.evidence_strength,
--             array_agg(distinct sc.name) as characteristics,
--             array_agg(distinct i.name) as beneficial_ingredients,
--             array_agg(distinct ic.ingredient_name) as caution_ingredients
--         FROM snp s
--         LEFT JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
--         LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
--         LEFT JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
--         LEFT JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
--         LEFT JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
--         LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
--         WHERE s.rsid = ANY(user_rsids)
--         GROUP BY s.gene, s.category, s.evidence_strength
--         ORDER BY
--             CASE
--                 WHEN s.evidence_strength = 'Strong' THEN 1
--                 WHEN s.evidence_strength = 'Moderate' THEN 2
--                 ELSE 3
--             END
--     ) LOOP
--         result_text := result_text || '<gene>';
--         result_text := result_text || '<name>' || gene_record.gene || '</name>';
--         result_text := result_text || '<category>' || gene_record.category || '</category>';
--         result_text := result_text || '<evidence>' || gene_record.evidence_strength || '</evidence>';
--
--         -- Add characteristics if they exist
--         IF gene_record.characteristics IS NOT NULL AND gene_record.characteristics[1] IS NOT NULL THEN
--             result_text := result_text || '<characteristics>';
--             FOR i IN 1..array_length(gene_record.characteristics, 1) LOOP
--                 IF gene_record.characteristics[i] IS NOT NULL THEN
--                     result_text := result_text || '<characteristic>' || gene_record.characteristics[i] || '</characteristic>';
--                 END IF;
--             END LOOP;
--             result_text := result_text || '</characteristics>';
--         END IF;
--
--         -- Add beneficial ingredients if they exist
--         IF gene_record.beneficial_ingredients IS NOT NULL AND gene_record.beneficial_ingredients[1] IS NOT NULL THEN
--             result_text := result_text || '<beneficial_ingredients>';
--             FOR i IN 1..array_length(gene_record.beneficial_ingredients, 1) LOOP
--                 IF gene_record.beneficial_ingredients[i] IS NOT NULL THEN
--                     result_text := result_text || '<ingredient>' || gene_record.beneficial_ingredients[i] || '</ingredient>';
--                 END IF;
--             END LOOP;
--             result_text := result_text || '</beneficial_ingredients>';
--         END IF;
--
--         -- Add caution ingredients if they exist
--         IF gene_record.caution_ingredients IS NOT NULL AND gene_record.caution_ingredients[1] IS NOT NULL THEN
--             result_text := result_text || '<caution_ingredients>';
--             FOR i IN 1..array_length(gene_record.caution_ingredients, 1) LOOP
--                 IF gene_record.caution_ingredients[i] IS NOT NULL THEN
--                     result_text := result_text || '<ingredient>' || gene_record.caution_ingredients[i] || '</ingredient>';
--                 END IF;
--             END LOOP;
--             result_text := result_text || '</caution_ingredients>';
--         END IF;
--
--         result_text := result_text || '</gene>';
--     END LOOP;
--
--     RETURN '<genetic_analysis>' || result_text || '</genetic_analysis>';
-- END;
-- $$;

-- --NEW VERSION--
CREATE OR REPLACE FUNCTION public.generate_genetic_analysis_section(user_variants text[])
RETURNS TABLE(report_text text, findings public.genetic_finding[])
LANGUAGE plpgsql AS
$function$
DECLARE
    analysis TEXT := E'YOUR GENETIC ANALYSIS\n\n';
    all_findings public.genetic_finding[];
    variant_record RECORD;
BEGIN
    -- Generate report text
    FOR variant_record IN
        SELECT * FROM format_genetic_analysis(user_variants)
    LOOP
        analysis := analysis
                    || E'\n=== '
                    || variant_record.section_title
                    || E' ===\n\n'
                    || variant_record.content
                    || E'\n\n';

        all_findings := array_append(all_findings, variant_record.variant_finding);
    END LOOP;

    RETURN QUERY SELECT analysis, all_findings;
END;
$function$;

--
-- Name: format_genetic_analysis(user_variants[]); Type: FUNCTION; Schema: public; Owner: cam
--
CREATE OR REPLACE FUNCTION public.format_genetic_analysis(user_variants text[])
RETURNS TABLE(
    section_title text,
    content text,
    priority integer,
    variant_finding public.genetic_finding
)
LANGUAGE plpgsql AS
$function$
BEGIN
    RETURN QUERY
    WITH variant_findings AS (
        SELECT DISTINCT ON (s.gene, s.category)
            s.gene,
            s.rsid,
            s.category,
            s.evidence_strength,
            s.effect,
            get_genetic_findings(s.rsid),
            CASE
                WHEN s.evidence_strength = 'Strong' THEN 1
                WHEN s.evidence_strength = 'Moderate' THEN 2
                ELSE 3
            END AS priority_order
        FROM snp s
        WHERE s.rsid = ANY(user_variants)
        ORDER BY s.gene, s.category, priority_order
    )
    SELECT
        format('%s (%s)', vf.gene, vf.category),
        format(
            E'Risk Level: %s\n\nWhat it means:\n%s\n\nAffects:\n%s\n\nRecommended Actions:\n%s',
            vf.evidence_strength,
            vf.effect,
            array_to_string((vf.get_genetic_findings).characteristics, ', '),
            CASE
                WHEN (vf.get_genetic_findings).beneficial_ingredients IS NOT NULL THEN
                    format(E'• Beneficial Ingredients:\n %s\n',
                        array_to_string((vf.get_genetic_findings).beneficial_ingredients, ', ')
                    )
                ELSE ''
            END ||
            CASE
                WHEN (vf.get_genetic_findings).caution_ingredients IS NOT NULL THEN
                    format(E'\n• Ingredients to Avoid/Use with Caution:\n %s',
                        array_to_string((vf.get_genetic_findings).caution_ingredients, ', ')
                    )
                ELSE ''
            END
        ),
        priority_order,
        get_genetic_findings
    FROM variant_findings vf
    ORDER BY priority_order, gene;
END;
$function$;

--
-- Name: get_genetic_findings(text); Type: FUNCTION; Schema: public; Owner: cam
--
CREATE OR REPLACE FUNCTION public.get_genetic_findings(variant_rsid text)
RETURNS public.genetic_finding
LANGUAGE plpgsql AS
$function$
DECLARE
    finding public.genetic_finding;
BEGIN
    -- Get basic variant info
    SELECT
        s.rsid,
        s.gene,
        s.category,
        s.evidence_strength,
        s.effect,
        array_agg(DISTINCT sc.name),
        array_agg(DISTINCT i.name),
        array_agg(DISTINCT ic.ingredient_name)
    INTO finding
    FROM snp s
    LEFT JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    LEFT JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
    LEFT JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
    LEFT JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
    LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    WHERE s.rsid = variant_rsid
    GROUP BY
        s.rsid,
        s.gene,
        s.category,
        s.evidence_strength,
        s.effect;

    RETURN finding;
END;
$function$;

--
-- Name: generate_summary_section(text[],public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--
CREATE OR REPLACE FUNCTION public.generate_summary_section(
    user_variants text[],
    genetic_data public.genetic_finding[] DEFAULT NULL::public.genetic_finding[]
)
RETURNS text
LANGUAGE plpgsql AS
$function$
DECLARE
    summary TEXT;
    high_risk_count INTEGER := 0;
    moderate_risk_count INTEGER := 0;
    weak_risk_count INTEGER := 0;
    categories TEXT[];
    focus_areas TEXT;
BEGIN
    -- Get counts and categories from genetic findings
    SELECT
        COUNT(*) FILTER (WHERE (unnest).evidence_strength = 'Strong'),
        COUNT(*) FILTER (WHERE (unnest).evidence_strength = 'Moderate'),
        COUNT(*) FILTER (WHERE (unnest).evidence_strength = 'Weak'),
        array_agg(DISTINCT (unnest).category)
    INTO
        high_risk_count,
        moderate_risk_count,
        weak_risk_count,
        categories
    FROM unnest(genetic_data);

    -- Generate focus areas from characteristics
    WITH trait_summary AS (
        SELECT DISTINCT
            category,
            trait,
            evidence_strength,
            CASE evidence_strength
                WHEN 'Strong' THEN 1
                WHEN 'Moderate' THEN 2
                ELSE 3
            END AS priority
        FROM unnest(genetic_data) gf,
             unnest(gf.characteristics) AS trait
        WHERE gf.characteristics IS NOT NULL
    ),
    grouped_traits AS (
        SELECT
            category,
            MIN(priority) AS category_priority,
            string_agg(trait, ', ' ORDER BY trait) AS traits
        FROM trait_summary
        GROUP BY category
    )
    SELECT
        string_agg(
            format(E'• %s: %s', category, traits),
            E'\n'
            ORDER BY category_priority, category
        )
    INTO focus_areas
    FROM grouped_traits;

    -- Generate summary text
    summary := format(
        E'
GENETIC PROFILE SUMMARY

Your DNA analysis revealed %s significant genetic variants that influence your skin health:

• %s high-priority variants requiring specific attention
• %s moderate-impact variants to consider
• %s lower-impact variants identified

Key Areas Affected:
%s

What This Means For You:
Based on your genetic profile, your skin care routine should focus on:

%s
',
        array_length(user_variants, 1),
        high_risk_count,
        moderate_risk_count,
        weak_risk_count,
        array_to_string(categories, ', '),
        coalesce(focus_areas, 'No specific focus areas identified.')
    );

    RETURN summary;
END;
$function$;




--
-- Name: generate_ingredient_recommendations(text[]); Type: FUNCTION; Schema: public; Owner: cam
--
CREATE OR REPLACE FUNCTION public.generate_ingredient_recommendations(user_rsids text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    result_text text := '';
    beneficial_text text := '';
    caution_text text := '';
    beneficial_record record;
    caution_record record;
BEGIN
    -- Generate beneficial ingredients section
    FOR beneficial_record IN (
        SELECT
            i.name as ingredient_name,
            sil.benefit_mechanism,
            sil.recommendation_strength,
            string_agg(distinct s.gene, ', ') as genes
        FROM snp s
        JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
        JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
        WHERE s.rsid = ANY(user_rsids)
        GROUP BY i.name, sil.benefit_mechanism, sil.recommendation_strength
        ORDER BY
            CASE
                WHEN sil.recommendation_strength = 'First-line' THEN 1
                WHEN sil.recommendation_strength = 'Second-line' THEN 2
                ELSE 3
            END
    ) LOOP
        beneficial_text := beneficial_text || '<ingredient>';
        beneficial_text := beneficial_text || '<name>' || beneficial_record.ingredient_name || '</name>';
        beneficial_text := beneficial_text || '<mechanism>' || beneficial_record.benefit_mechanism || '</mechanism>';
        beneficial_text := beneficial_text || '<strength>' || beneficial_record.recommendation_strength || '</strength>';
        beneficial_text := beneficial_text || '<genes>' || beneficial_record.genes || '</genes>';
        beneficial_text := beneficial_text || '</ingredient>';
    END LOOP;

    -- Generate caution ingredients section
    FOR caution_record IN (
        SELECT
            ic.ingredient_name,
            ic.risk_mechanism,
            ic.category,
            ic.alternative_ingredients,
            string_agg(distinct s.gene, ', ') as genes
        FROM snp s
        JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
        JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
        WHERE s.rsid = ANY(user_rsids)
        GROUP BY ic.ingredient_name, ic.risk_mechanism, ic.category, ic.alternative_ingredients
        ORDER BY ic.category
    ) LOOP
        caution_text := caution_text || '<ingredient>';
        caution_text := caution_text || '<name>' || caution_record.ingredient_name || '</name>';
        caution_text := caution_text || '<risk>' || caution_record.risk_mechanism || '</risk>';
        caution_text := caution_text || '<category>' || caution_record.category || '</category>';
        caution_text := caution_text || '<genes>' || caution_record.genes || '</genes>';

        IF caution_record.alternative_ingredients IS NOT NULL THEN
            caution_text := caution_text || '<alternatives>' || caution_record.alternative_ingredients || '</alternatives>';
        END IF;

        caution_text := caution_text || '</ingredient>';
    END LOOP;

    -- Combine both sections
    result_text := '<ingredient_recommendations>';
    result_text := result_text || '<beneficial>' || beneficial_text || '</beneficial>';
    result_text := result_text || '<cautions>' || caution_text || '</cautions>';
    result_text := result_text || '</ingredient_recommendations>';

    RETURN result_text;
END;
$$;


--
-- Name: generate_summary_section(text[]); Type: FUNCTION; Schema: public; Owner: cam
--
--
-- CREATE OR REPLACE FUNCTION public.generate_summary_section(user_rsids text[]) RETURNS text
--     LANGUAGE plpgsql
--     AS $$
-- DECLARE
--     result_text text;
--     gene_count integer;
--     primary_genes text[];
--     characteristic_count integer;
--     top_characteristics text[];
--     beneficial_count integer;
--     caution_count integer;
-- BEGIN
--     -- Get gene statistics
--     SELECT
--         COUNT(DISTINCT s.gene),
--         ARRAY_AGG(DISTINCT s.gene ORDER BY s.evidence_strength)
--     INTO gene_count, primary_genes
--     FROM snp s
--     WHERE s.rsid = ANY(user_rsids)
--     AND s.evidence_strength IN ('Strong', 'Moderate');
--
--     IF gene_count > 3 THEN
--         primary_genes := primary_genes[1:3];
--     END IF;
--
--     -- Get characteristic statistics
--     SELECT
--         COUNT(DISTINCT sc.characteristic_id),
--         ARRAY_AGG(DISTINCT sc.name)
--     INTO characteristic_count, top_characteristics
--     FROM snp s
--     JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
--     JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
--     WHERE s.rsid = ANY(user_rsids)
--     AND s.evidence_strength IN ('Strong', 'Moderate');
--
--     IF characteristic_count > 3 THEN
--         top_characteristics := top_characteristics[1:3];
--     END IF;
--
--     -- Get ingredient recommendation counts
--     SELECT COUNT(DISTINCT i.ingredient_id)
--     INTO beneficial_count
--     FROM snp s
--     JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
--     JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
--     WHERE s.rsid = ANY(user_rsids);
--
--     SELECT COUNT(DISTINCT ic.caution_id)
--     INTO caution_count
--     FROM snp s
--     JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
--     JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
--     WHERE s.rsid = ANY(user_rsids);
--
--     -- Generate summary text
--     result_text := '<summary>';
--
--     -- Genes summary
--     result_text := result_text || '<gene_count>' || gene_count || '</gene_count>';
--     result_text := result_text || '<primary_genes>';
--     IF array_length(primary_genes, 1) > 0 THEN
--         FOR i IN 1..array_length(primary_genes, 1) LOOP
--             result_text := result_text || '<gene>' || primary_genes[i] || '</gene>';
--         END LOOP;
--     END IF;
--     result_text := result_text || '</primary_genes>';
--
--     -- Characteristics summary
--     result_text := result_text || '<characteristic_count>' || characteristic_count || '</characteristic_count>';
--     result_text := result_text || '<primary_characteristics>';
--     IF array_length(top_characteristics, 1) > 0 THEN
--         FOR i IN 1..array_length(top_characteristics, 1) LOOP
--             result_text := result_text || '<characteristic>' || top_characteristics[i] || '</characteristic>';
--         END LOOP;
--     END IF;
--     result_text := result_text || '</primary_characteristics>';
--
--     -- Ingredient recommendations summary
--     result_text := result_text || '<beneficial_count>' || beneficial_count || '</beneficial_count>';
--     result_text := result_text || '<caution_count>' || caution_count || '</caution_count>';
--
--     result_text := result_text || '</summary>';
--
--     RETURN result_text;
-- END;
-- $$;
