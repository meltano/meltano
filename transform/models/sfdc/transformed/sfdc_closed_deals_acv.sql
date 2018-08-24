WITH sfdc_opportunity as (

  SELECT * FROM {{ref('sfdc_opportunity_xf')}}

), sfdc_account as (

  SELECT * FROM {{ref('sfdc_account')}}

), joined as (

    SELECT sfdc_opportunity.sales_type,
           sfdc_opportunity.close_date,
           sfdc_opportunity.opportunity_id,
           sfdc_opportunity.owner,
           sfdc_opportunity.sales_path,
           sfdc_opportunity.acv,
           sfdc_account.account_segment,
           sfdc_opportunity.closed_deals
    FROM sfdc_opportunity 
      INNER JOIN sfdc_account  
      ON sfdc_account.account_id = sfdc_opportunity.account_id
    WHERE sfdc_opportunity.sales_type!= 'Reseller'
    AND   sfdc_opportunity.stage_name IN ('Closed Won')
    AND  (sfdc_opportunity.is_deleted IS FALSE)

)

SELECT owner, 
       sales_path,
       sales_type,
       account_segment, 
       close_date,
       SUM(acv) AS acv,
       SUM(closed_deals) AS closed_deals
FROM joined
GROUP BY 1, 2, 3, 4, 5