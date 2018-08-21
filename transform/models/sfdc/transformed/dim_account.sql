{{
  config({
    "materialized":"table",
    "post-hook": [
       "ALTER TABLE {{ this }} ADD PRIMARY KEY(id)"
    ]
  })
}}

with account as (
		select * from {{ ref('account') }}
)

SELECT row_number() OVER (
                          ORDER BY sfdc_account_id) AS id,
       COALESCE(sfdc_account_id, 'Unknown') as sfdc_account_id,
       COALESCE(name, 'Unknown') as name,
       COALESCE(industry, 'Unknown') as industry,
       COALESCE(type, 'Unknown') as type,
       COALESCE(Sales_Segmentation__c, 'Unknown') as sales_segmentation,
       COALESCE(ultimate_parent_Sales_Segmentation, 'Unknown') as ultimate_parent_sales_segmentation,
       COALESCE(ultimate_parent_name, 'Unknown') as ultimate_parent_name,
       Is_LAU,
       health_score,
       health_score_reasons,
       technical_account_manager,
       new_sales_segmentation,
       count_open_opportunities
FROM account 