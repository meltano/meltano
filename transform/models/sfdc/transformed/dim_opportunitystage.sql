{{
  config({
    "materialized":"table",
    "post-hook": [
       "ALTER TABLE {{ this }} ADD PRIMARY KEY(stage_id)"
    ]
  })
}}

WITH stages AS (
  SELECT * FROM {{ ref("sfdc_opportunitystage") }}
)

SELECT
    *
FROM stages