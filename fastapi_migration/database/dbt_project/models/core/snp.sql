{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['rsid'], 'unique': false}
    ]
  )
}}

SELECT
  snp_id,
  rsid,
  gene,
  risk_allele,
  effect,
  evidence_strength,
  category
FROM {{ source('raw', 'snp') }}