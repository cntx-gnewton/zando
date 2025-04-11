{{
  config(
    materialized='table'
  )
}}

SELECT
  caution_id,
  ingredient_name,
  category,
  risk_mechanism,
  affected_characteristic,
  alternative_ingredients
FROM {{ source('raw', 'ingredientcaution') }}