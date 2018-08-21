with quotelineitems as (
    SELECT opportunity_id
           FROM {{ ref('quotelineitems') }}
),

count_of_opp_items as(

    SELECT oli.opportunityid,
           count(*) AS num_line_tems
    FROM sfdc.opportunitylineitem oli
    WHERE oli.isdeleted = FALSE
    GROUP BY oli.opportunityid
),

opplineitems as (

SELECT oli.id,
       oli.opportunityid AS opportunity_id,
       p.name AS product,
       'Unknown'::text AS period,
       oli.quantity,
       CASE
           WHEN sum(oli.totalprice) OVER (PARTITION BY o.id) = 0 THEN 0
           WHEN i.num_line_tems > 1 THEN round((o.Incremental_ACV__c * (oli.totalprice / sum(oli.totalprice) OVER (PARTITION BY o.id)))::numeric, 4)
           ELSE o.Incremental_ACV__c
       END AS iacv,
       CASE
           WHEN sum(oli.totalprice) OVER (PARTITION BY o.id) = 0 THEN 0
           WHEN i.num_line_tems > 1 THEN round((o.ACV__c * (oli.totalprice / sum(oli.totalprice) OVER (PARTITION BY o.id)))::numeric, 4)
           ELSE o.ACV__c
       END AS acv,
       CASE
           WHEN sum(oli.totalprice) OVER (PARTITION BY o.id) = 0 THEN 0
           WHEN i.num_line_tems > 1 THEN round((o.Renewal_ACV__c * (oli.totalprice / sum(oli.totalprice) OVER (PARTITION BY o.id)))::numeric, 4)
           ELSE o.Renewal_ACV__c
       END AS renewal_acv,
       CASE
           WHEN sum(oli.totalprice) OVER (PARTITION BY o.id) = 0 THEN 0
           WHEN i.num_line_tems > 1 THEN round((o.Amount * (oli.totalprice / sum(oli.totalprice) OVER (PARTITION BY o.id)))::numeric, 4)
           ELSE o.Amount
       END AS tcv
FROM sfdc.opportunitylineitem oli
JOIN sfdc.opportunity o ON oli.opportunityid = o.id::text
LEFT JOIN sfdc.pricebookentry pbe ON oli.pricebookentryid = pbe.id
LEFT JOIN sfdc.product2 p ON pbe.product2id = p.id
JOIN count_of_opp_items i ON i.opportunityid = o.id::text
WHERE o.isdeleted = FALSE
  AND oli.isdeleted = FALSE
  AND NOT (o.id::text IN
             (SELECT opportunity_id
              FROM quotelineitems))
  )

select * from opplineitems
