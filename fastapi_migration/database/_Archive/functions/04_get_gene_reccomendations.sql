-- Drop the function if it exists
DROP FUNCTION IF EXISTS public.get_gene_recommendations(text);

-- Helper function to get gene-specific recommendations
CREATE OR REPLACE FUNCTION public.get_gene_recommendations(variant_rsid TEXT)
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

    -- Return the recommendations or a default message if none are found
    RETURN COALESCE(recommendations, 'No specific ingredient recommendations available.');
END;
$$ LANGUAGE plpgsql;