{{
  config(
    materialized='table'
  )
}}

SELECT
  snp_id,
  characteristic_id,
  effect_direction,
  evidence_strength
FROM {{ source('raw', 'snp_characteristic_link') }}