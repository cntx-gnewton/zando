{{
  config(
    materialized='table'
  )
}}

SELECT
  characteristic_id,
  name,
  description,
  measurement_method
FROM {{ source('raw', 'skincharacteristic') }}