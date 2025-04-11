{{
  config(
    materialized='view'
  )
}}

SELECT
  s.rsid,
  s.gene,
  s.risk_allele,
  s.effect,
  s.evidence_strength,
  s.category,
  ARRAY_AGG(DISTINCT sc.name) AS characteristics,
  ARRAY_AGG(DISTINCT i.name) AS beneficial_ingredients,
  ARRAY_AGG(DISTINCT ic.ingredient_name) AS caution_ingredients
FROM {{ ref('snp') }} s
LEFT JOIN {{ ref('snp_characteristic_link') }} scl ON s.snp_id = scl.snp_id
LEFT JOIN {{ ref('skin_characteristic') }} sc ON scl.characteristic_id = sc.characteristic_id
LEFT JOIN {{ ref('snp_ingredient_link') }} sil ON s.snp_id = sil.snp_id
LEFT JOIN {{ ref('ingredient') }} i ON sil.ingredient_id = i.ingredient_id
LEFT JOIN {{ ref('snp_ingredient_caution_link') }} sicl ON s.snp_id = sicl.snp_id
LEFT JOIN {{ ref('ingredient_caution') }} ic ON sicl.caution_id = ic.caution_id
GROUP BY s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category