-- Drop the function if it exists
DROP FUNCTION IF EXISTS public.format_genetic_analysis(text[]);

-- Create or replace the function
CREATE OR REPLACE FUNCTION public.format_genetic_analysis(user_variants text[])
  RETURNS TABLE(section_title text, content text, priority integer, variant_finding genetic_finding)
  LANGUAGE plpgsql
AS $function$
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
$function$;