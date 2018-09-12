
with quotelineitems as (
    SELECT *
           FROM {{ ref('quotelineitems') }} 
),

opplineitems as (
  SELECT *
              FROM  {{ ref('opplineitems') }} 
),

nolineitems as (
  SELECT *  FROM {{ ref('nolineitems') }}
)

SELECT * FROM quotelineitems
UNION ALL
SELECT * FROM opplineitems
UNION ALL
SELECT * FROM nolineitems