{{
  config(
    materialized='table'
  )
}}

SELECT
  characteristic_id,
  condition_id,
  relationship_type
FROM {{ source('raw', 'characteristic_condition_link') }}