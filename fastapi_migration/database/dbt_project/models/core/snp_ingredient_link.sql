{{
  config(
    materialized='table'
  )
}}

SELECT
  snp_id,
  ingredient_id,
  benefit_mechanism,
  recommendation_strength,
  evidence_level
FROM {{ source('raw', 'snp_ingredient_link') }}