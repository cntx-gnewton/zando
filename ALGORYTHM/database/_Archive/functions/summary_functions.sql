-- Drop existing functions
DROP FUNCTION IF EXISTS count_variants_by_impact();
DROP FUNCTION IF EXISTS generate_summary_section(text[]);
DROP FUNCTION IF EXISTS generate_focus_areas(text[]);

-- Define the custom type
CREATE TYPE genetic_finding AS (
    gene_name TEXT,
    variant TEXT,
    position INTEGER,
    description TEXT
);

-- Function to summarize genetic findings
CREATE OR REPLACE FUNCTION generate_summary_section(
    user_variants TEXT[],
    genetic_data genetic_finding[] 
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



CREATE OR REPLACE FUNCTION generate_genetic_analysis_section(user_variants TEXT[])
RETURNS TEXT AS $$
DECLARE
    analysis TEXT;
    variant_record RECORD;
BEGIN
    analysis := E'YOUR GENETIC ANALYSIS\n\n';
    
    FOR variant_record IN
        SELECT * FROM format_genetic_analysis(user_variants)
    LOOP
        analysis := analysis ||
            E'\n=== ' || variant_record.section_title || E' ===\n\n' ||
            variant_record.content || E'\n\n';
    END LOOP;
    
    RETURN analysis;
END;
$$ LANGUAGE plpgsql;


-- Function to format genetic variant details with better formatting
CREATE OR REPLACE FUNCTION format_genetic_analysis(user_variants TEXT[])
RETURNS TABLE (
    section_title TEXT,
    content TEXT,
    priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH variant_analysis AS (
        SELECT
            s.gene,
            s.rsid,
            s.category,
            s.evidence_strength,
            s.effect,
            string_agg(DISTINCT sc.name, ', ') as affected_traits,
            CASE
                WHEN s.evidence_strength = 'Strong' THEN 1
                WHEN s.evidence_strength = 'Moderate' THEN 2
                ELSE 3
            END as priority_order
        FROM snp s
        JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
        JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
        WHERE s.rsid = ANY(user_variants)
        GROUP BY s.gene, s.rsid, s.category, s.evidence_strength, s.effect
    )
    SELECT
        format('%s (%s)', va.gene, va.category) as section_title,
        format(E'Risk Level: %s\n\nWhat it means:\n%s\n\nAffects:\n%s\n\nRecommended Actions:\n%s',
            va.evidence_strength,
            va.effect,
            va.affected_traits,
            get_gene_recommendations(va.rsid)
        ) as content,
        va.priority_order as priority
    FROM variant_analysis va
    ORDER BY va.priority_order, va.category;
END;
$$ LANGUAGE plpgsql;

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