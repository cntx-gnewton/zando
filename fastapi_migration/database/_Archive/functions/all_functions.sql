-- Helper function to get gene-specific recommendations
CREATE OR REPLACE FUNCTION get_gene_recommendations(variant_rsid TEXT)
RETURNS TEXT AS $$
DECLARE
    recommendations TEXT;
BEGIN
    WITH gene_recs AS (
        -- Get beneficial ingredients
        SELECT
            'Beneficial Ingredients' as type,
            1 as sort_order,
            string_agg(DISTINCT i.name, ', ') as items
        FROM snp s
        JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
        JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
        WHERE s.rsid = variant_rsid
        GROUP BY 1, 2 -- Group by type and sort_order
        UNION ALL
        -- Get ingredients to avoid
        SELECT
            'Ingredients to Avoid/Use with Caution' as type,
            2 as sort_order,
            string_agg(DISTINCT ic.ingredient_name, ', ') as items
        FROM snp s
        JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
        JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
        WHERE s.rsid = variant_rsid
        GROUP BY 1, 2 -- Group by type and sort_order
    )
    SELECT string_agg(
        CASE
            WHEN items IS NOT NULL AND items != ''
            THEN '• ' || type || ':\n ' || items
            ELSE NULL
        END,
        E'\n\n'
        ORDER BY sort_order -- Move ORDER BY into string_agg
    )
    INTO recommendations
    FROM gene_recs
    WHERE items IS NOT NULL AND items != '';
    
    RETURN COALESCE(recommendations, 'No specific ingredient recommendations available.');
END;
$$ LANGUAGE plpgsql;




-- Drop the function if it exists
DROP FUNCTION IF EXISTS generate_genetic_analysis_section(text[]);

-- Create or replace the function
CREATE OR REPLACE FUNCTION generate_genetic_analysis_section(user_variants text[])
  RETURNS TABLE(report_text text, findings genetic_finding[])
  LANGUAGE plpgsql
AS $function$
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
$function$;


-- Drop the function if it exists
DROP FUNCTION IF EXISTS public.generate_summary_section(text[], genetic_finding[]);

-- Create or replace the function
CREATE OR REPLACE FUNCTION public.generate_summary_section(
    user_variants text[],
    genetic_data genetic_finding[] DEFAULT NULL::genetic_finding[]
)
RETURNS text
LANGUAGE plpgsql
AS $function$
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
$function$;