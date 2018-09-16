
with quotelineitems as (
    SELECT opportunity_id
           FROM {{ ref('quotelineitems') }} 
),

opplineitems as (
  SELECT opportunity_id
              FROM  {{ ref('opplineitems') }} 
)

SELECT o.id,
       o.id AS opportunity_id,
       COALESCE(o.products_purchased__c, 'Unknown'::text) AS product,
       'Unknown'::text AS period,
       1 AS qty,
       o.Incremental_ACV__c AS iacv,
       o.ACV__c as ACV,
       o.Renewal_ACV__c as Renewal_ACV,
       Amount as TCV
FROM sfdc.opportunity o
WHERE o.isdeleted = FALSE
  AND NOT (o.id::text IN
             (SELECT opportunity_id
              FROM quotelineitems))
  AND NOT (o.id::text IN
             (SELECT opportunity_id
              FROM opplineitems))