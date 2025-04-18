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