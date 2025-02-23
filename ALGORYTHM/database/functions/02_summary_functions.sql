-- Drop existing functions
DROP FUNCTION IF EXISTS count_variants_by_impact();
DROP FUNCTION IF EXISTS generate_summary_section(text[]);
DROP FUNCTION IF EXISTS generate_focus_areas(text[]);

-- Function to summarize genetic findings
CREATE OR REPLACE FUNCTION generate_summary_section(
    user_variants TEXT[],
    genetic_data genetic_finding[] DEFAULT NULL
) RETURNS TEXT AS $$
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
$$ LANGUAGE plpgsql;

-- Function to get detailed category impacts
CREATE OR REPLACE FUNCTION get_category_impacts(genetic_data genetic_finding[])
RETURNS TABLE (
    category TEXT,
    impact_level TEXT,
    affected_traits TEXT[],
    gene_count INTEGER
) AS $$
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
$$ LANGUAGE plpgsql;
