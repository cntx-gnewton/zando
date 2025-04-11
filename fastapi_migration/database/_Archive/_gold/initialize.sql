--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: genetic_finding; Type: TYPE; Schema: public; Owner: cam
--


DROP FUNCTION IF EXISTS public.analyze_genetic_risks(text[]);
DROP FUNCTION IF EXISTS public.apply_report_formatting(text, text, jsonb);
DROP FUNCTION IF EXISTS public.calculate_ingredient_score(integer, text[]);
DROP FUNCTION IF EXISTS public.calculate_product_compatibility(integer, text[], jsonb, jsonb);
DROP FUNCTION IF EXISTS public.calculate_routine_score(integer, jsonb);
DROP FUNCTION IF EXISTS public.format_gene_entry(text, text, text);
DROP FUNCTION IF EXISTS public.format_genetic_analysis(text[]);
DROP FUNCTION IF EXISTS public.format_genetic_summary(text[], text);
DROP FUNCTION IF EXISTS public.format_ingredient_list(text[]);
DROP FUNCTION IF EXISTS public.format_risk_level(text);
DROP FUNCTION IF EXISTS public.format_section_header(text);
DROP FUNCTION IF EXISTS public.format_warning_entry(text, text);
DROP FUNCTION IF EXISTS public.generate_complete_report(text[]);
DROP FUNCTION IF EXISTS public.generate_detailed_recommendations_section(text[]);
DROP FUNCTION IF EXISTS public.generate_genetic_analysis_section(text[]);
DROP FUNCTION IF EXISTS public.generate_recommendations_section(text[], public.genetic_finding[]);
DROP FUNCTION IF EXISTS public.generate_report_from_path(text);
DROP FUNCTION IF EXISTS public.generate_skincare_report(text[]);
DROP FUNCTION IF EXISTS public.generate_skincare_routine(text[]);
DROP FUNCTION IF EXISTS public.generate_summary_section(text[], public.genetic_finding[]);
DROP FUNCTION IF EXISTS public.get_categorized_recommendations(text[], public.genetic_finding[]);
DROP FUNCTION IF EXISTS public.get_category_impacts(public.genetic_finding[]);
DROP FUNCTION IF EXISTS public.get_genetic_findings(text);
DROP FUNCTION IF EXISTS public.get_ingredient_cautions(text[], public.genetic_finding[]);
DROP FUNCTION IF EXISTS public.get_ingredients_to_avoid(text[]);
DROP FUNCTION IF EXISTS public.get_or_create_benefit(text);
DROP FUNCTION IF EXISTS public.get_recommended_ingredients(text[]);
DROP FUNCTION IF EXISTS public.get_report_sections();
DROP FUNCTION IF EXISTS public.get_section_style(text);
DROP FUNCTION IF EXISTS public.get_variant_detailed_effects(text);
DROP FUNCTION IF EXISTS public.parse_report_sections(text);
DROP FUNCTION IF EXISTS public.prepare_pdf_report(text);
DROP FUNCTION IF EXISTS public.process_ancestry_file(text);
DROP FUNCTION IF EXISTS public.process_dna_file(text);
DROP FUNCTION IF EXISTS public.process_dna_file_to_report(text);
DROP FUNCTION IF EXISTS public.split_and_clean_list(text);
DROP FUNCTION IF EXISTS public.structure_pdf_content(text);
DROP FUNCTION IF EXISTS public.validate_dna_file_format(text);
DROP TYPE IF EXISTS public.genetic_finding CASCADE;
DROP TYPE IF EXISTS public.pdf_style CASCADE;
DROP TYPE IF EXISTS public.routine_step_type CASCADE;

DROP TABLE IF EXISTS public.characteristic_condition_link CASCADE;
DROP TABLE IF EXISTS public.condition_ingredient_link CASCADE;
DROP TABLE IF EXISTS public.snp_characteristic_link CASCADE;
DROP TABLE IF EXISTS public.snp_ingredient_link CASCADE;
DROP TABLE IF EXISTS public.snp_ingredientcaution_link CASCADE;
DROP TABLE IF EXISTS public.ingredient CASCADE;
DROP TABLE IF EXISTS public.ingredientcaution CASCADE;
DROP TABLE IF EXISTS public.skincondition CASCADE;
DROP TABLE IF EXISTS public.skincharacteristic CASCADE;
DROP TABLE IF EXISTS public.snp CASCADE;



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


--
-- Name: analyze_genetic_risks(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.analyze_genetic_risks(user_rsids text[]) RETURNS TABLE(gene text, category text, evidence_strength text, affected_characteristics text[], risk_level text)
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
--
-- Name: apply_report_formatting(text, text, jsonb); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.apply_report_formatting(section_type text, content text, additional_data jsonb) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    formatted_content TEXT;
    variants TEXT[];
BEGIN
    -- Extract variants array from JSONB
    IF additional_data ? 'variants' THEN
        variants := ARRAY(
            SELECT jsonb_array_elements_text(additional_data->'variants')
        );
    ELSE
        variants := ARRAY[]::TEXT[];
    END IF;

    CASE section_type
        WHEN 'overview' THEN
            formatted_content := format_genetic_summary(variants, content);
        WHEN 'analysis' THEN
            formatted_content := content;
        WHEN 'recommendations' THEN
            formatted_content := content;
        WHEN 'cautions' THEN
            formatted_content := content;
        ELSE
            formatted_content := content;
    END CASE;

    RETURN formatted_content;
END;
$$;



--
-- Name: calculate_ingredient_score(integer, text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.calculate_ingredient_score(target_ingredient_id integer, user_snps text[]) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    score DECIMAL := 0;
BEGIN
    -- Score beneficial effects
    SELECT COALESCE(SUM(
        CASE 
            WHEN i.evidence_level = 'Strong' THEN 3
            WHEN i.evidence_level = 'Moderate' THEN 2
            ELSE 1
        END *
        CASE
            WHEN sil.recommendation_strength = 'First-line' THEN 2
            WHEN sil.recommendation_strength = 'Second-line' THEN 1.5
            ELSE 1
        END
    ), 0)
    INTO score
    FROM ingredient i
    JOIN snp_ingredient_link sil ON i.ingredient_id = sil.ingredient_id
    JOIN snp s ON sil.snp_id = s.snp_id
    WHERE i.ingredient_id = target_ingredient_id
    AND s.rsid = ANY(user_snps);

    -- Subtract points for cautions
    SELECT score - COALESCE(SUM(
        CASE 
            WHEN ic.category = 'Avoid' THEN 5
            WHEN ic.category = 'Use with Caution' THEN 2
            ELSE 0
        END
    ), 0)
    INTO score
    FROM ingredientcaution ic
    JOIN snp_ingredientcaution_link sicl ON ic.caution_id = sicl.caution_id
    JOIN snp s ON sicl.snp_id = s.snp_id
    WHERE s.rsid = ANY(user_snps)
    AND EXISTS (
        SELECT 1
        FROM ingredient i
        WHERE i.ingredient_id = target_ingredient_id
        AND i.name = ic.ingredient_name
    );

    RETURN score;
END;
$$;


--
-- Name: calculate_product_compatibility(integer, text[], jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.calculate_product_compatibility(product_id integer, user_snps text[], user_characteristics jsonb DEFAULT '{}'::jsonb, user_routine_needs jsonb DEFAULT '{}'::jsonb) RETURNS TABLE(total_score numeric, ingredient_score numeric, routine_score numeric, characteristic_score numeric, recommendation_level text, key_benefits text[], cautions text[], explanation jsonb)
    LANGUAGE plpgsql
    AS $$
DECLARE
    ing_score DECIMAL := 0;
    rtn_score DECIMAL := 0;
    chr_score DECIMAL := 0;
BEGIN
    -- Calculate ingredient compatibility
    SELECT COALESCE(SUM(
        calculate_ingredient_score(pil.ingredient_id, user_snps) *
        CASE 
            WHEN pil.is_active THEN 1.5
            ELSE 1
        END *
        COALESCE(pil.concentration_percentage, 1) / 100
    ), 0)
    INTO ing_score
    FROM product_ingredient_link pil
    WHERE pil.product_id = calculate_product_compatibility.product_id;

    -- Calculate routine fit score
    rtn_score := calculate_routine_score(product_id, user_routine_needs);

    -- Calculate characteristics match score
    SELECT COALESCE(SUM(
        CASE 
            WHEN pb.category = ANY(ARRAY(SELECT jsonb_object_keys(user_characteristics))) THEN 2
            ELSE 0.5
        END
    ), 0)
    INTO chr_score
    FROM product_benefit_link pbl
    JOIN product_benefit pb ON pbl.benefit_id = pb.benefit_id
    WHERE pbl.product_id = calculate_product_compatibility.product_id;

    RETURN QUERY SELECT
        ing_score + rtn_score + chr_score,
        ing_score,
        rtn_score,
        chr_score,
        CASE 
            WHEN (ing_score + rtn_score + chr_score) >= 8 THEN 'Highly Recommended'
            WHEN (ing_score + rtn_score + chr_score) >= 5 THEN 'Recommended'
            WHEN (ing_score + rtn_score + chr_score) >= 2 THEN 'Suitable'
            WHEN (ing_score + rtn_score + chr_score) >= 0 THEN 'Use with Caution'
            ELSE 'Not Recommended'
        END,
        ARRAY(
            SELECT DISTINCT pb.name
            FROM product_benefit_link pbl
            JOIN product_benefit pb ON pbl.benefit_id = pb.benefit_id
            WHERE pbl.product_id = calculate_product_compatibility.product_id
            AND pbl.strength = 'Primary'
        ),
        ARRAY(
            SELECT DISTINCT ic.ingredient_name
            FROM product_ingredient_link pil
            JOIN ingredient i ON pil.ingredient_id = i.ingredient_id
            JOIN ingredientcaution ic ON ic.ingredient_name = i.name
            WHERE pil.product_id = calculate_product_compatibility.product_id
        ),
        jsonb_build_object(
            'ingredient_compatibility', ing_score,
            'routine_fit', rtn_score,
            'characteristic_match', chr_score,
            'total_score', (ing_score + rtn_score + chr_score)
        );
END;
$$;




--
-- Name: calculate_routine_score(integer, jsonb); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.calculate_routine_score(product_id integer, user_routine_needs jsonb) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    score DECIMAL := 0;
BEGIN
    SELECT COALESCE(
        CASE 
            WHEN prp.routine_step::text = user_routine_needs->>'needed_step' THEN 3
            WHEN prp.routine_step IS NOT NULL THEN 1
            ELSE 0
        END, 0)
    INTO score
    FROM product_routine_position prp
    WHERE prp.product_id = calculate_routine_score.product_id;

    RETURN score;
END;
$$;




--
-- Name: format_gene_entry(text, text, text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_gene_entry(gene text, category text, evidence text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN format(E'%s (%s)\n%s\n',
        gene,
        category,
        format_risk_level(evidence)
    );
END;
$$;



--
-- Name: format_genetic_analysis(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_genetic_analysis(user_variants text[]) RETURNS TABLE(section_title text, content text, priority integer, variant_finding public.genetic_finding)
    LANGUAGE plpgsql
    AS $$
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
            END as priority_order
        FROM snp s
        WHERE s.rsid = ANY(user_variants)
        ORDER BY s.gene, s.category, priority_order
    )
    SELECT 
        format('%s (%s)', vf.gene, vf.category),
        format(E'Risk Level: %s\n\nWhat it means:\n%s\n\nAffects:\n%s\n\nRecommended Actions:\n%s',
            vf.evidence_strength,
            vf.effect,
            array_to_string((vf.get_genetic_findings).characteristics, ', '),
            CASE 
                WHEN (vf.get_genetic_findings).beneficial_ingredients IS NOT NULL THEN
                    format(E'• Beneficial Ingredients:\n  %s\n', 
                        array_to_string((vf.get_genetic_findings).beneficial_ingredients, ', '))
                ELSE ''
            END ||
            CASE 
                WHEN (vf.get_genetic_findings).caution_ingredients IS NOT NULL THEN
                    format(E'\n• Ingredients to Avoid/Use with Caution:\n  %s', 
                        array_to_string((vf.get_genetic_findings).caution_ingredients, ', '))
                ELSE ''
            END
        ),
        priority_order,
        get_genetic_findings
    FROM variant_findings vf
    ORDER BY priority_order, gene;
END;
$$;



--
-- Name: format_genetic_summary(text[], text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_genetic_summary(user_variants text[], section_content text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    formatted_text TEXT;
    variant_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO variant_count 
    FROM unnest(user_variants);

    formatted_text := format(
        E'Based on analysis of %s genetic variants:\n\n%s',
        variant_count,
        section_content
    );

    RETURN formatted_text;
END;
$$;



--
-- Name: format_ingredient_list(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_ingredient_list(ingredients text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN array_to_string(
        array(
            SELECT format(E'• %s', ingredient) 
            FROM unnest(ingredients) AS ingredient
        ),
        E'\n'
    );
END;
$$;



--
-- Name: format_risk_level(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_risk_level(level text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN CASE 
        WHEN level = 'Strong' THEN '🔴 High Risk'
        WHEN level = 'Moderate' THEN '🟡 Moderate Risk'
        WHEN level = 'Weak' THEN '🟢 Low Risk'
        ELSE '⚪ Unknown Risk'
    END;
END;
$$;



--
-- Name: format_section_header(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_section_header(title text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN format(E'\n%s\n%s\n', 
        title,
        repeat('=', length(title))
    );
END;
$$;



--
-- Name: format_warning_entry(text, text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.format_warning_entry(ingredient text, reason text) RETURNS text
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN format(E'⚠️ %s\n   %s', ingredient, coalesce(reason, 'Use with caution'));
END;
$$;



--
-- Name: generate_complete_report(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_complete_report(user_variants text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    report TEXT := '';
    section_record RECORD;
BEGIN
    -- Get report sections in correct order
    FOR section_record IN (
        SELECT * FROM get_report_sections() ORDER BY display_order
    ) LOOP
        -- Add formatted section header
        report := report || format_section_header(section_record.section_name);
        
        -- Generate content based on section type
        CASE section_record.section_type
            WHEN 'overview' THEN
                report := report || generate_summary_section(user_variants);
            WHEN 'analysis' THEN
                report := report || generate_genetic_analysis_section(user_variants);
            WHEN 'recommendations' THEN
                report := report || generate_recommendations_section(user_variants);
            WHEN 'cautions' THEN
                report := report || get_ingredient_cautions(user_variants);
            ELSE
                report := report || format(E'Section type %s not implemented.\n', section_record.section_type);
        END CASE;

        -- Add section spacing
        report := report || E'\n\n';
    END LOOP;

    RETURN report;
END;
$$;



--
-- Name: generate_detailed_recommendations_section(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_detailed_recommendations_section(user_variants text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    recommendations TEXT := E'DETAILED GENETIC ANALYSIS AND RECOMMENDATIONS\n\n';
    variant_record RECORD;
    detail_record RECORD;
    ingredient_record RECORD;
    caution_text TEXT;
BEGIN
    FOR variant_record IN (
        SELECT 
            s.rsid::TEXT,
            s.gene::TEXT,
            s.category::TEXT,
            s.evidence_strength::TEXT,
            s.effect::TEXT
        FROM snp s
        WHERE s.rsid = ANY(user_variants)
        ORDER BY 
            CASE s.evidence_strength 
                WHEN 'Strong' THEN 1
                WHEN 'Moderate' THEN 2
                ELSE 3
            END,
            s.category
    ) LOOP
        -- Add section header for each variant
        recommendations := recommendations ||
            format(E'\n=== %s Gene Analysis (%s) ===\n', 
                variant_record.gene, 
                variant_record.category);
            
        -- Add evidence strength and primary effect
        recommendations := recommendations ||
            format(E'Evidence Strength: %s\n', variant_record.evidence_strength) ||
            format(E'Primary Effect: %s\n\n', variant_record.effect);
            
        -- Add detailed effects on skin characteristics
        recommendations := recommendations || E'How This Affects Your Skin:\n';
        
        FOR detail_record IN (
            SELECT * FROM get_variant_detailed_effects(variant_record.rsid)
        ) LOOP
            recommendations := recommendations ||
                format(E'• %s: %s\n  %s\n',
                    detail_record.characteristic_name,
                    detail_record.effect_direction,
                    coalesce(detail_record.description, 'No detailed description available.')
                );
        END LOOP;
        
        -- Add ingredient recommendations section
        recommendations := recommendations || E'\nRecommended Ingredients:\n';
        
        FOR ingredient_record IN (
            SELECT 
                i.name::TEXT,
                i.mechanism::TEXT,
                sil.benefit_mechanism::TEXT
            FROM snp s
            JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
            JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
            WHERE s.rsid = variant_record.rsid
        ) LOOP
            recommendations := recommendations ||
                format(E'• %s\n  How it helps: %s\n  Mechanism: %s\n',
                    ingredient_record.name,
                    coalesce(ingredient_record.benefit_mechanism, 'Supports overall skin health'),
                    coalesce(ingredient_record.mechanism, 'Multiple pathways')
                );
        END LOOP;
        
        -- Add cautions section if any exist
        SELECT string_agg(
            format(E'• %s (%s)\n  Reason: %s\n',
                ic.ingredient_name::TEXT,
                ic.category::TEXT,
                ic.risk_mechanism::TEXT
            ),
            E'\n'
        )
        INTO caution_text
        FROM snp s
        JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
        JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
        WHERE s.rsid = variant_record.rsid;
        
        IF caution_text IS NOT NULL THEN
            recommendations := recommendations || E'\nIngredients to Watch:\n' || caution_text;
        END IF;
        
        recommendations := recommendations || E'\n';
    END LOOP;

    RETURN recommendations;
END;
$$;



--
-- Name: generate_genetic_analysis_section(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_genetic_analysis_section(user_variants text[]) RETURNS TABLE(report_text text, findings public.genetic_finding[])
    LANGUAGE plpgsql
    AS $$
DECLARE
    analysis TEXT := E'YOUR GENETIC ANALYSIS\n\n';
    all_findings genetic_finding[];
    variant_record RECORD;
BEGIN
    -- Generate report text
    FOR variant_record IN 
        SELECT * FROM format_genetic_analysis(user_variants)
    LOOP
        analysis := analysis || 
            E'\n=== ' || variant_record.section_title || E' ===\n\n' ||
            variant_record.content || E'\n\n';
            
        all_findings := array_append(all_findings, variant_record.variant_finding);
    END LOOP;

    RETURN QUERY SELECT analysis, all_findings;
END;
$$;



--
-- Name: generate_recommendations_section(text[], public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_recommendations_section(user_variants text[], genetic_data public.genetic_finding[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    recommendations TEXT := E'PERSONALIZED INGREDIENT RECOMMENDATIONS\n\n';
    rec RECORD;
    cautions TEXT;
BEGIN
    -- Get categorized recommendations
    FOR rec IN 
        SELECT * FROM get_categorized_recommendations(user_variants, genetic_data)
    LOOP
        -- Only add categories that have ingredients
        IF rec.ingredients IS NOT NULL AND array_length(rec.ingredients, 1) > 0 THEN
            recommendations := recommendations ||
                format(E'=== For %s ===\n', rec.category) ||
                format(E'Priority Level: %s\n',
                    CASE 
                        WHEN rec.priority = 1 THEN 'High Priority'
                        WHEN rec.priority = 2 THEN 'Medium Priority'
                        ELSE 'Supporting'
                    END) ||
                E'Key Ingredients:\n' ||
                array_to_string(rec.ingredients, E'\n• ', E'• ') || E'\n' ||
                format(E'Why These Work: %s\n', rec.reason) ||
                format(E'Evidence Level: %s\n\n', rec.evidence_level);
        END IF;
    END LOOP;

    -- Add cautions section
    cautions := get_ingredient_cautions(user_variants, genetic_data);
    IF cautions IS NOT NULL AND cautions != '' THEN
        recommendations := recommendations || E'\nINGREDIENTS TO WATCH\n' || cautions;
    END IF;

    RETURN recommendations;
END;
$$;



--
-- Name: generate_report_from_path(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_report_from_path(file_content text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    report_text TEXT;
    variants TEXT[];
BEGIN
    -- Extract rsids from file content
    WITH parsed_content AS (
        SELECT unnest(string_to_array(file_content, E'\n')) AS line_text
    ),
    valid_lines AS (
        SELECT TRIM(line_text) as line_text
        FROM parsed_content 
        WHERE line_text != ''
        AND line_text NOT LIKE '#%'
        AND line_text NOT LIKE 'rsid%'
        AND line_text ~ '^rs[0-9]+'
    ),
    extracted_rsids AS (
        SELECT TRIM(split_part(line_text, E'\t', 1)) as rsid
        FROM valid_lines
    )
    SELECT array_agg(rsid) INTO variants
    FROM extracted_rsids;

    -- Debug output
    RAISE NOTICE 'Found variants: %', variants;

    -- Generate report using extracted variants
    IF variants IS NULL OR array_length(variants, 1) = 0 THEN
        RAISE EXCEPTION 'No valid variants found in file content';
    END IF;

    report_text := generate_complete_report(variants);
    
    RETURN report_text;
EXCEPTION
    WHEN OTHERS THEN
        RETURN format('Error generating report: %s', SQLERRM);
END;
$$;



--
-- Name: generate_skincare_report(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_skincare_report(user_rsids text[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    report TEXT;
    genetic_risk_row RECORD;
    routine_step_row RECORD;
    ingredient_row RECORD;
    caution_row RECORD;
BEGIN
    report := E'\n=== PERSONALIZED SKINCARE REPORT ===\n\n';
    
    -- 1. Genetic Risk Assessment
    report := report || E'GENETIC RISK ASSESSMENT\n';
    report := report || E'------------------------\n';
    FOR genetic_risk_row IN (
        SELECT * FROM analyze_genetic_risks(user_rsids)
    ) LOOP
        report := report || format(
            E'Gene: %s (%s)\n' ||
            E'Risk Level: %s\n' ||
            E'Affects: %s\n\n',
            genetic_risk_row.gene,
            genetic_risk_row.category,
            genetic_risk_row.risk_level,
            array_to_string(genetic_risk_row.affected_characteristics, ', ')
        );
    END LOOP;

    -- 2. Key Recommendations
    report := report || E'DAILY SKINCARE ROUTINE\n';
    report := report || E'---------------------\n';
    FOR routine_step_row IN (
        SELECT * FROM generate_skincare_routine(user_rsids)
        ORDER BY 
            CASE routine_step
                WHEN 'Cleanser' THEN 1
                WHEN 'Treatment' THEN 2
                WHEN 'Moisturizer' THEN 3
                WHEN 'Sun Protection' THEN 4
            END
    ) LOOP
        report := report || format(
            E'%s:\n' ||
            E'  Primary Options: %s\n' ||
            E'  Alternative Options: %s\n' ||
            E'  Notes: %s\n\n',
            routine_step_row.routine_step,
            array_to_string(array_remove(routine_step_row.primary_recommendations, NULL), ', '),
            array_to_string(array_remove(routine_step_row.alternative_recommendations, NULL), ', '),
            routine_step_row.notes
        );
    END LOOP;

    -- 3. Ingredient Recommendations
    report := report || E'RECOMMENDED INGREDIENTS\n';
    report := report || E'----------------------\n';
    FOR ingredient_row IN (
        SELECT * FROM get_recommended_ingredients(user_rsids)
        WHERE evidence_level = 'Strong'
        ORDER BY recommendation_strength DESC
    ) LOOP
        report := report || format(
            E'%s:\n' ||
            E'  Benefits: %s\n' ||
            E'  Evidence Level: %s\n\n',
            ingredient_row.ingredient_name,
            array_to_string(ingredient_row.beneficial_for, ', '),
            ingredient_row.evidence_level
        );
    END LOOP;

    -- 4. Ingredients to Avoid
    report := report || E'INGREDIENTS TO AVOID/USE WITH CAUTION\n';
    report := report || E'----------------------------------\n';
    FOR caution_row IN (
        SELECT * FROM get_ingredients_to_avoid(user_rsids)
        ORDER BY 
            CASE caution_level
                WHEN 'Avoid' THEN 1
                WHEN 'Use with Caution' THEN 2
            END
    ) LOOP
        report := report || format(
            E'%s (%s):\n' ||
            E'  Reason: %s\n' ||
            E'  Alternatives: %s\n\n',
            caution_row.ingredient_name,
            caution_row.caution_level,
            caution_row.risk_mechanism,
            caution_row.alternatives
        );
    END LOOP;

    -- 5. Additional Notes
    report := report || E'ADDITIONAL NOTES\n';
    report := report || E'----------------\n';
    report := report || E'- Always patch test new products before full application\n';
    report := report || E'- Introduce new products one at a time\n';
    report := report || E'- Monitor skin response and adjust routine as needed\n';
    report := report || E'- Consider seasonal adjustments to your routine\n';
    
    RETURN report;
END;
$$;



--
-- Name: generate_skincare_routine(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_skincare_routine(user_rsids text[]) RETURNS TABLE(routine_step text, primary_recommendations text[], alternative_recommendations text[], ingredients_to_avoid text[], notes text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH user_concerns AS (
        SELECT DISTINCT
            sc.name::text as characteristic,
            s.evidence_strength::text,
            cond.name::text as condition
        FROM snp s
        JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
        JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
        JOIN characteristic_condition_link ccl ON sc.characteristic_id = ccl.characteristic_id
        JOIN skincondition cond ON ccl.condition_id = cond.condition_id
        WHERE s.rsid = ANY(user_rsids)
    )
    SELECT
        step.routine_step::text,
        ARRAY_AGG(DISTINCT 
            CASE WHEN cil.recommendation_strength = 'First-line' 
            THEN i.name::text END
        ) as primary_recs,
        ARRAY_AGG(DISTINCT 
            CASE WHEN cil.recommendation_strength = 'Second-line' 
            THEN i.name::text END
        ) as alternative_recs,
        ARRAY_AGG(DISTINCT ic.ingredient_name::text) as avoid,
        MAX(step.notes::text) as step_notes
    FROM (VALUES 
        ('Cleanser'::text, 1, 'Gentle cleansing based on skin characteristics'::text),
        ('Treatment'::text, 2, 'Target specific skin concerns'::text),
        ('Moisturizer'::text, 3, 'Barrier support and hydration'::text),
        ('Sun Protection'::text, 4, 'UV protection based on sensitivity'::text)
    ) as step(routine_step, step_order, notes)
    CROSS JOIN user_concerns uc
    LEFT JOIN condition_ingredient_link cil ON TRUE
    LEFT JOIN ingredient i ON cil.ingredient_id = i.ingredient_id
    LEFT JOIN snp_ingredientcaution_link sicl ON TRUE
    LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    GROUP BY step.routine_step, step.step_order
    ORDER BY step.step_order;
END;
$$;



--
-- Name: generate_summary_section(text[], public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.generate_summary_section(user_variants text[], genetic_data public.genetic_finding[] DEFAULT NULL::public.genetic_finding[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
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
            END as priority
        FROM unnest(genetic_data) gf,
        unnest(gf.characteristics) as trait
        WHERE gf.characteristics IS NOT NULL
    ),
    grouped_traits AS (
        SELECT 
            category,
            MIN(priority) as category_priority,
            string_agg(trait, ', ' ORDER BY trait) as traits
        FROM trait_summary
        GROUP BY category
    )
    SELECT string_agg(
        format(E'• %s: %s', category, traits),
        E'\n'
        ORDER BY category_priority, category
    )
    INTO focus_areas
    FROM grouped_traits;

    -- Generate summary text
    summary := format(E'
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
$$;



--
-- Name: get_categorized_recommendations(text[], public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_categorized_recommendations(user_variants text[], genetic_data public.genetic_finding[]) RETURNS TABLE(category text, priority integer, ingredients text[], reason text, evidence_level text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH relevant_categories AS (
        -- Get unique categories from genetic findings
        SELECT DISTINCT 
            (unnest(genetic_data)).category as cat,
            (unnest(genetic_data)).evidence_strength as strength
    ),
    unnested_ingredients AS (
        SELECT 
            gf.category,
            gf.evidence_strength,
            gf.effect,
            i.ingredient
        FROM unnest(genetic_data) gf
        CROSS JOIN LATERAL unnest(gf.beneficial_ingredients) as i(ingredient)
        WHERE gf.beneficial_ingredients IS NOT NULL
    )
    SELECT 
        rc.cat,
        CASE 
            WHEN rc.strength = 'Strong' THEN 1
            WHEN rc.strength = 'Moderate' THEN 2
            ELSE 3
        END as priority,
        array_agg(DISTINCT ui.ingredient) as ingredients,
        string_agg(DISTINCT ui.effect, '; ') as reason,
        MAX(ui.evidence_strength) as evidence_level
    FROM relevant_categories rc
    LEFT JOIN unnested_ingredients ui ON ui.category = rc.cat
    GROUP BY rc.cat, rc.strength
    ORDER BY priority, rc.cat;
END;
$$;



--
-- Name: get_category_impacts(public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_category_impacts(genetic_data public.genetic_finding[]) RETURNS TABLE(category text, impact_level text, affected_traits text[], gene_count integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        gf.category,
        MAX(gf.evidence_strength) as impact_level,
        array_agg(DISTINCT trait) as affected_traits,
        COUNT(DISTINCT gf.gene) as gene_count
    FROM unnest(genetic_data) gf
    CROSS JOIN LATERAL unnest(gf.characteristics) as trait
    GROUP BY gf.category
    ORDER BY 
        CASE MAX(gf.evidence_strength)
            WHEN 'Strong' THEN 1
            WHEN 'Moderate' THEN 2
            ELSE 3
        END,
        gf.category;
END;
$$;



--
-- Name: get_genetic_findings(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_genetic_findings(variant_rsid text) RETURNS public.genetic_finding
    LANGUAGE plpgsql
    AS $$
DECLARE
    finding genetic_finding;
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
    GROUP BY s.rsid, s.gene, s.category, s.evidence_strength, s.effect;
    
    RETURN finding;
END;
$$;



--
-- Name: get_ingredient_cautions(text[], public.genetic_finding[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_ingredient_cautions(user_variants text[], genetic_data public.genetic_finding[]) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    cautions TEXT := '';
BEGIN
    WITH unique_cautions AS (
        -- Get unique caution ingredients from genetic findings
        SELECT DISTINCT 
            unnest(gf.caution_ingredients) as ingredient_name,
            gf.category,
            gf.evidence_strength
        FROM unnest(genetic_data) gf
        WHERE gf.caution_ingredients IS NOT NULL
    ),
    formatted_cautions AS (
        SELECT 
            ic.ingredient_name,
            ic.category as caution_category,
            ic.risk_mechanism,
            ic.alternative_ingredients,
            uc.evidence_strength,
            ic.category = 'Avoid' as is_avoid
        FROM unique_cautions uc
        JOIN ingredientcaution ic ON ic.ingredient_name = uc.ingredient_name
    )
    SELECT string_agg(
        format(E'%s: %s\n Why: %s\n Alternatives: %s\n',
            CASE 
                WHEN is_avoid THEN '⚠️ AVOID'
                ELSE '⚡ USE WITH CAUTION'
            END,
            ingredient_name,
            risk_mechanism,
            alternative_ingredients
        ),
        E'\n'
        ORDER BY is_avoid DESC, evidence_strength
    )
    INTO cautions
    FROM formatted_cautions;

    RETURN cautions;
END;
$$;



--
-- Name: get_ingredients_to_avoid(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_ingredients_to_avoid(user_rsids text[]) RETURNS TABLE(ingredient_name text, caution_level text, risk_mechanism text, alternatives text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        ic.ingredient_name::text,
        ic.category::text as caution_level,
        ic.risk_mechanism::text,
        ic.alternative_ingredients::text
    FROM snp s
    JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
    JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    WHERE s.rsid = ANY(user_rsids);
END;
$$;



--
-- Name: get_or_create_benefit(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_or_create_benefit(benefit_name text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    benefit_id INTEGER;
BEGIN
    SELECT pb.benefit_id INTO benefit_id
    FROM product_benefit pb
    WHERE pb.name = benefit_name;
    
    IF benefit_id IS NULL THEN
        INSERT INTO product_benefit (name)
        VALUES (benefit_name)
        RETURNING benefit_id INTO benefit_id;
    END IF;
    
    RETURN benefit_id;
END;
$$;



--
-- Name: get_recommended_ingredients(text[]); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_recommended_ingredients(user_rsids text[]) RETURNS TABLE(ingredient_name text, recommendation_strength text, evidence_level text, beneficial_for text[], cautions text[])
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH user_snps AS (
        SELECT snp_id, evidence_strength
        FROM snp
        WHERE rsid = ANY(user_rsids)
    )
    SELECT 
        i.name::text,
        MAX(sil.recommendation_strength)::text as rec_strength,
        i.evidence_level::text,
        ARRAY_AGG(DISTINCT sc.name::text) as benefits,
        ARRAY_AGG(DISTINCT ic.risk_mechanism::text) as cautions
    FROM user_snps us
    JOIN snp_ingredient_link sil ON us.snp_id = sil.snp_id
    JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
    LEFT JOIN snp_characteristic_link scl ON us.snp_id = scl.snp_id
    LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    LEFT JOIN snp_ingredientcaution_link sicl ON us.snp_id = sicl.snp_id
    LEFT JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
    GROUP BY i.name, i.evidence_level;
END;
$$;



--
-- Name: get_report_sections(); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_report_sections() RETURNS TABLE(section_id integer, section_name character varying, display_order integer, section_type character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rs.section_id,
        rs.section_name,
        rs.display_order,
        rs.section_type
    FROM report_sections rs
    WHERE rs.is_active = true
    ORDER BY rs.display_order;
END;
$$;



--
-- Name: get_section_style(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_section_style(section_title text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN CASE 
        WHEN section_title ILIKE '%summary%' THEN
            jsonb_build_object(
                'font_name', 'Helvetica',
                'font_size', 12,
                'alignment', 'left',
                'spacing', 1.2,
                'section_color', '#2C3E50'
            )
        WHEN section_title ILIKE '%analysis%' THEN
            jsonb_build_object(
                'font_name', 'Helvetica',
                'font_size', 11,
                'alignment', 'left',
                'spacing', 1.3,
                'section_color', '#34495E'
            )
        WHEN section_title ILIKE '%recommendations%' THEN
            jsonb_build_object(
                'font_name', 'Helvetica',
                'font_size', 11,
                'alignment', 'left',
                'spacing', 1.3,
                'section_color', '#27AE60'
            )
        WHEN section_title ILIKE '%cautions%' THEN
            jsonb_build_object(
                'font_name', 'Helvetica',
                'font_size', 11,
                'alignment', 'left',
                'spacing', 1.3,
                'section_color', '#E74C3C'
            )
        ELSE
            jsonb_build_object(
                'font_name', 'Helvetica',
                'font_size', 11,
                'alignment', 'left',
                'spacing', 1.2,
                'section_color', '#2C3E50'
            )
    END;
END;
$$;



--
-- Name: get_variant_detailed_effects(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.get_variant_detailed_effects(variant_rsid text) RETURNS TABLE(characteristic_name text, effect_direction text, description text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sc.name::TEXT,
        scl.effect_direction::TEXT,
        sc.description::TEXT
    FROM snp s
    JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    WHERE s.rsid = variant_rsid;
END;
$$;



--
-- Name: parse_report_sections(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.parse_report_sections(report_text text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $_$
DECLARE
    sections JSONB := '[]'::jsonb;
    current_section TEXT;
    section_content TEXT;
    section_lines TEXT[];
    line TEXT;
    in_section BOOLEAN := false;
BEGIN
    -- Split report into lines
    section_lines := string_to_array(report_text, E'\n');
    
    -- Process each line
    FOREACH line IN ARRAY section_lines
    LOOP
        -- Check for section headers (lines with ===)
        IF line ~ '^={3,}$' AND NOT in_section THEN
            -- Previous line was section title
            current_section := section_lines[array_position(section_lines, line) - 1];
            in_section := true;
            section_content := '';
            CONTINUE;
        END IF;
        
        -- If we're in a section, accumulate content
        IF in_section THEN
            -- Check for next section start
            IF line ~ '^={3,}$' THEN
                -- Add completed section to JSON
                sections := sections || jsonb_build_object(
                    'title', current_section,
                    'content', trim(section_content),
                    'style', get_section_style(current_section)
                );
                current_section := section_lines[array_position(section_lines, line) - 1];
                section_content := '';
            ELSE
                section_content := section_content || line || E'\n';
            END IF;
        END IF;
    END LOOP;
    
    -- Add final section if exists
    IF current_section IS NOT NULL THEN
        sections := sections || jsonb_build_object(
            'title', current_section,
            'content', trim(section_content),
            'style', get_section_style(current_section)
        );
    END IF;
    
    RETURN sections;
END;
$_$;



--
-- Name: prepare_pdf_report(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.prepare_pdf_report(file_content text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    report_text TEXT;
    pdf_content JSONB;
BEGIN
    -- Generate the report
    report_text := generate_complete_report(file_content);
    
    -- Structure the content for PDF
    pdf_content := structure_pdf_content(report_text);
    
    RETURN pdf_content;
END;
$$;



--
-- Name: process_ancestry_file(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.process_ancestry_file(file_content text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    complete_report TEXT := '';
    analysis_section TEXT;
    relevant_variants TEXT[];
    genetic_findings genetic_finding[];
BEGIN
    -- Get relevant variants using process_dna_file
    SELECT array_agg(rsid), array_agg((
        rsid, 
        category, 
        evidence_strength, 
        effect,
        NULL::text[], -- characteristics
        NULL::text[], -- beneficial_ingredients
        NULL::text[]  -- caution_ingredients
    )::genetic_finding)
    FROM process_dna_file(file_content)
    WHERE is_relevant = true
    INTO relevant_variants, genetic_findings;

    -- Validate we found relevant variants
    IF relevant_variants IS NULL OR array_length(relevant_variants, 1) = 0 THEN
        RAISE EXCEPTION 'No matching variants found in our database';
    END IF;

    -- Update genetic_findings with full data
    SELECT array_agg(gf.*)
    FROM unnest(relevant_variants) rv
    CROSS JOIN LATERAL get_genetic_findings(rv) gf
    INTO genetic_findings;

    -- Get genetic analysis and findings
    SELECT ga.report_text
    INTO analysis_section
    FROM generate_genetic_analysis_section(relevant_variants) ga;
    
    -- Build complete report
    complete_report := 
        format(E'\nSummary\n=======\n%s\n', 
            generate_summary_section(relevant_variants, genetic_findings));

    complete_report := complete_report || 
        format(E'\nGenetic Analysis\n================\n%s\n', 
            analysis_section);

    complete_report := complete_report || 
        format(E'\nPersonalized Recommendations\n============================\n%s\n',
            generate_recommendations_section(relevant_variants, genetic_findings));
    
    RETURN complete_report;
EXCEPTION
    WHEN OTHERS THEN
        RETURN format('Error processing DNA file: %s', SQLERRM);
END;
$$;



--
-- Name: process_dna_file(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.process_dna_file(file_content text) RETURNS TABLE(rsid text, genotype text, is_relevant boolean, evidence_strength text, category text, effect text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    lines text[];
    line text;
    parts text[];
    start_processing boolean := false;
BEGIN
    -- Split the file content into lines
    lines := string_to_array(file_content, E'\n');
    
    -- Process each line
    FOREACH line IN ARRAY lines
    LOOP
        -- Skip empty lines and comments
        IF line = '' OR starts_with(line, '#') THEN
            CONTINUE;
        END IF;
        
        -- Skip header line but start processing after it
        IF line = 'rsid	chromosome	position	allele1	allele2' THEN
            start_processing := true;
            CONTINUE;
        END IF;
        
        -- Process data lines
        IF start_processing THEN
            -- Split the line into parts
            parts := string_to_array(line, E'\t');
            
            -- Check if this SNP exists in our database AND has risk allele
            SELECT 
                s.rsid,
                parts[4] || parts[5],
                CASE 
                    WHEN parts[4] = s.risk_allele OR parts[5] = s.risk_allele THEN true
                    ELSE false
                END,
                s.evidence_strength,
                s.category,
                s.effect
            FROM snp s
            WHERE s.rsid = parts[1]
            INTO rsid, genotype, is_relevant, evidence_strength, category, effect;
            
            IF FOUND AND is_relevant THEN
                RETURN NEXT;
            END IF;
        END IF;
    END LOOP;
END;
$$;



--
-- Name: process_dna_file_to_report(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.process_dna_file_to_report(file_content text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    report_content JSONB;
BEGIN
    -- Validate file format
    IF NOT validate_dna_file_format(file_content) THEN
        RAISE EXCEPTION 'Invalid DNA file format. Please ensure file is in correct format.';
    END IF;
    
    -- Generate and structure report
    report_content := prepare_pdf_report(file_content);
    
    RETURN report_content;
EXCEPTION
    WHEN OTHERS THEN
        RETURN jsonb_build_object(
            'error', SQLERRM,
            'detail', 'Error processing DNA file. Please check file format and try again.'
        );
END;
$$;



--
-- Name: split_and_clean_list(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.split_and_clean_list(input_text text) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN ARRAY(
        SELECT DISTINCT trim(both ' "''' FROM unnest)
        FROM unnest(string_to_array(
            CASE 
                WHEN input_text LIKE '[%]' THEN 
                    trim(both '[]' FROM input_text)
                ELSE 
                    input_text
            END, 
            ','
        ))
        WHERE trim(both ' "''' FROM unnest) != ''
    );
END;
$$;



--
-- Name: structure_pdf_content(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.structure_pdf_content(report_content text) RETURNS jsonb
    LANGUAGE plpgsql
    AS $$
DECLARE
    structured_content JSONB;
    section_style pdf_style;
BEGIN
    -- Define default styles
    section_style := ('Helvetica', 12, 'left', 1.2, false)::pdf_style;
    
    -- Structure the content with styling information
    structured_content := jsonb_build_object(
        'metadata', jsonb_build_object(
            'title', 'Genetic Skin Analysis Report',
            'created_at', CURRENT_TIMESTAMP,
            'version', '1.0'
        ),
        'styling', jsonb_build_object(
            'header_style', jsonb_build_object(
                'font_name', 'Helvetica-Bold',
                'font_size', 14,
                'alignment', 'center',
                'spacing', 1.5
            ),
            'body_style', jsonb_build_object(
                'font_name', section_style.font_name,
                'font_size', section_style.font_size,
                'alignment', section_style.alignment,
                'spacing', section_style.spacing
            ),
            'risk_levels', jsonb_build_object(
                'high', '#FF0000',
                'moderate', '#FFA500',
                'low', '#008000'
            )
        ),
        'content', jsonb_build_object(
            'sections', parse_report_sections(report_content)
        )
    );

    RETURN structured_content;
END;
$$;



--
-- Name: validate_dna_file_format(text); Type: FUNCTION; Schema: public; Owner: cam
--

CREATE FUNCTION public.validate_dna_file_format(file_content text) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    header_line TEXT;
    first_data_line TEXT;
    lines TEXT[];
BEGIN
    -- Split content into lines
    lines := string_to_array(file_content, E'\n');
    
    -- Find header line
    SELECT line INTO header_line
    FROM unnest(lines) AS line
    WHERE line LIKE '%rsid%chromosome%position%allele1%allele2%'
    LIMIT 1;
    
    -- Get first non-empty data line
    SELECT line INTO first_data_line
    FROM unnest(lines) AS line
    WHERE line != '' 
    AND line NOT LIKE '#%'
    AND line != header_line
    LIMIT 1;
    
    -- Validate format
    RETURN header_line IS NOT NULL 
        AND first_data_line IS NOT NULL 
        AND array_length(string_to_array(first_data_line, E'\t'), 1) >= 5;
END;
$$;



SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: characteristic_condition_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.characteristic_condition_link (
    characteristic_id integer NOT NULL,
    condition_id integer NOT NULL,
    relationship_type character varying
);



--
-- Name: condition_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.condition_ingredient_link (
    condition_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    recommendation_strength character varying,
    guidance_notes text,
    CONSTRAINT condition_ingredient_link_recommendation_strength_check CHECK (((recommendation_strength)::text = ANY ((ARRAY['First-line'::character varying, 'Second-line'::character varying, 'Adjuvant'::character varying])::text[])))
);



--
-- Name: ingredient; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.ingredient (
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

CREATE TABLE public.ingredientcaution (
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

CREATE TABLE public.skincondition (
    condition_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    severity_scale text
);



--
-- Name: snp; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.snp (
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

CREATE TABLE public.snp_characteristic_link (
    snp_id integer NOT NULL,
    characteristic_id integer NOT NULL,
    effect_direction character varying,
    evidence_strength character varying,
    CONSTRAINT snp_characteristic_link_effect_direction_check CHECK (((effect_direction)::text = ANY ((ARRAY['Increases'::character varying, 'Decreases'::character varying, 'Modulates'::character varying])::text[])))
);



--
-- Name: snp_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.snp_ingredient_link (
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

CREATE TABLE public.snp_ingredientcaution_link (
    snp_id integer NOT NULL,
    caution_id integer NOT NULL,
    evidence_level character varying,
    notes text,
    CONSTRAINT snp_ingredientcaution_link_evidence_level_check CHECK (((evidence_level)::text = ANY ((ARRAY['Strong'::character varying, 'Moderate'::character varying, 'Weak'::character varying])::text[])))
);



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
-- Name: product; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product (
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

CREATE TABLE public.product_aspect (
    aspect_id integer NOT NULL,
    name character varying NOT NULL,
    category character varying,
    description text
);



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
-- Name: product_aspect_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_aspect_link (
    product_id integer NOT NULL,
    aspect_id integer NOT NULL
);



--
-- Name: product_benefit; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_benefit (
    benefit_id integer NOT NULL,
    name character varying NOT NULL,
    category character varying,
    description text
);



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
-- Name: product_benefit_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_benefit_link (
    product_id integer NOT NULL,
    benefit_id integer NOT NULL,
    strength character varying,
    CONSTRAINT product_benefit_link_strength_check CHECK (((strength)::text = ANY ((ARRAY['Primary'::character varying, 'Secondary'::character varying])::text[])))
);



--
-- Name: product_concern; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_concern (
    concern_id integer NOT NULL,
    name character varying NOT NULL,
    related_characteristic character varying,
    description text
);



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
-- Name: product_concern_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_concern_link (
    product_id integer NOT NULL,
    concern_id integer NOT NULL
);



--
-- Name: product_ingredient_link; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_ingredient_link (
    product_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    is_active boolean DEFAULT false,
    concentration_percentage numeric
);



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
-- Name: product_routine_position; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_routine_position (
    position_id integer NOT NULL,
    product_id integer,
    routine_step public.routine_step_type NOT NULL,
    step_order integer
);



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
-- Name: product_genetic_suitability; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.product_genetic_suitability (
    product_id integer NOT NULL,
    snp_id integer NOT NULL,
    suitability_score integer,
    reason text,
    CONSTRAINT product_genetic_suitability_suitability_score_check CHECK (((suitability_score >= '-2'::integer) AND (suitability_score <= 2)))
);



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
-- Name: report_log; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.report_log (
    log_id integer NOT NULL,
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    report_summary text
);



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
-- Name: report_sections; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.report_sections (
    section_id integer NOT NULL,
    section_name character varying NOT NULL,
    display_order integer NOT NULL,
    section_type character varying NOT NULL,
    is_active boolean DEFAULT true
);



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
-- Name: skincharacteristic; Type: TABLE; Schema: public; Owner: cam
--

CREATE TABLE public.skincharacteristic (
    characteristic_id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    measurement_method text
);



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
