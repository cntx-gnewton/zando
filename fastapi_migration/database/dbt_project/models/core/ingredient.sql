{{
  config(
    materialized='table'
  )
}}

SELECT
  ingredient_id,
  name,
  mechanism,
  evidence_level,
  contraindications
FROM {{ source('raw', 'ingredient') }}