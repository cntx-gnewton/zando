-- generate_summary_section.sql
SELECT pg_get_functiondef(oid)
FROM pg_proc
WHERE proname = 'generate_summary_section';

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