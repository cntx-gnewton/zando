{{
  config(
    materialized='table'
  )
}}

SELECT
  snp_id,
  caution_id,
  evidence_level,
  notes
FROM {{ source('raw', 'snp_ingredientcaution_link') }}