{{
  config(
    materialized='table'
  )
}}

SELECT
  condition_id,
  name,
  description,
  severity_scale
FROM {{ source('raw', 'skincondition') }}