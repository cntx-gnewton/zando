-- Analysis Summary Function for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to generate an analysis summary as JSON
CREATE OR REPLACE FUNCTION generate_analysis_summary(
    p_user_id INTEGER,
    p_file_id INTEGER,
    p_rsids TEXT[]
) RETURNS JSONB AS $$
DECLARE
    summary JSONB;
    snp_data JSONB;
    characteristic_data JSONB;
    ingredient_data JSONB;
    caution_data JSONB;
    rsid TEXT;
BEGIN
    -- Initialize result structure
    summary := jsonb_build_object(
        'user_id', p_user_id,
        'file_id', p_file_id,
        'generated_at', NOW(),
        'total_snps', array_length(p_rsids, 1),
        'snps', jsonb_build_array()
    );
    
    -- Process each SNP
    FOREACH rsid IN ARRAY p_rsids LOOP
        -- Get SNP data
        SELECT jsonb_build_object(
            'rsid', s.rsid,
            'gene', s.gene,
            'risk_allele', s.risk_allele,
            'effect', s.effect,
            'evidence_strength', s.evidence_strength,
            'category', s.category
        ) INTO snp_data
        FROM snp s
        WHERE s.rsid = rsid;
        
        -- Skip if SNP not found
        CONTINUE WHEN snp_data IS NULL;
        
        -- Get characteristics
        SELECT jsonb_agg(
            jsonb_build_object(
                'name', sc.name,
                'effect_direction', scl.effect_direction,
                'evidence_strength', scl.evidence_strength
            )
        ) INTO characteristic_data
        FROM snp s
        JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
        JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
        WHERE s.rsid = rsid;
        
        -- Get beneficial ingredients
        SELECT jsonb_agg(
            jsonb_build_object(
                'name', i.name,
                'benefit_mechanism', sil.benefit_mechanism,
                'recommendation_strength', sil.recommendation_strength,
                'evidence_level', sil.evidence_level
            )
        ) INTO ingredient_data
        FROM snp s
        JOIN snp_ingredient_link sil ON s.snp_id = sil.snp_id
        JOIN ingredient i ON sil.ingredient_id = i.ingredient_id
        WHERE s.rsid = rsid;
        
        -- Get caution ingredients
        SELECT jsonb_agg(
            jsonb_build_object(
                'name', ic.ingredient_name,
                'category', ic.category,
                'risk_mechanism', ic.risk_mechanism,
                'relationship_notes', sicl.relationship_notes,
                'evidence_level', sicl.evidence_level
            )
        ) INTO caution_data
        FROM snp s
        JOIN snp_ingredientcaution_link sicl ON s.snp_id = sicl.snp_id
        JOIN ingredientcaution ic ON sicl.caution_id = ic.caution_id
        WHERE s.rsid = rsid;
        
        -- Add to summary with all related data
        summary := jsonb_set(
            summary,
            '{snps}',
            (summary->'snps') || jsonb_build_object(
                'snp', snp_data,
                'characteristics', COALESCE(characteristic_data, '[]'::jsonb),
                'beneficial_ingredients', COALESCE(ingredient_data, '[]'::jsonb),
                'caution_ingredients', COALESCE(caution_data, '[]'::jsonb)
            )
        );
    END LOOP;
    
    RETURN summary;
END;
$$ LANGUAGE plpgsql;