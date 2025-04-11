{{
  config(
    materialized='table'
  )
}}

SELECT
  condition_id,
  ingredient_id,
  recommendation_strength,
  guidance_notes
FROM {{ source('raw', 'condition_ingredient_link') }}