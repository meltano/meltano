{{
  config({
    "materialized":"table",
    "post-hook": [
       "DROP INDEX IF EXISTS {{ this.schema }}.idx_f_opportunity_stageid",
       "DROP INDEX IF EXISTS {{ this.schema }}.idx_f_opportunity_closedate",
       "DROP INDEX IF EXISTS {{ this.schema }}.idx_f_opportunity_leadource",
       "DROP INDEX IF EXISTS {{ this.schema }}.idx_f_opportunity_account_id",
       "CREATE INDEX IF NOT EXISTS idx_f_opportunity_stageid ON {{ this }}(opportunity_stage_id)",
       "CREATE INDEX IF NOT EXISTS idx_f_opportunity_closedate ON {{ this}}(opportunity_closedate)",
       "CREATE INDEX IF NOT EXISTS idx_f_opportunity_leadource ON {{ this }}(lead_source_id)",
       "CREATE INDEX IF NOT EXISTS idx_f_opportunity_account_id ON {{ this }}(account_id)"
    ]
  })
}}


with lineitems as (
		select * from {{ ref('lineitems') }}

),
oppstage as (
		select * from {{ ref('dim_opportunitystage') }}

),

opportunity as (
	  select * from {{ ref('opportunity') }}

),

leadsource as (
    select * from {{ ref('dim_leadsource') }}
),

account as (
    select * from {{ ref('dim_account') }}
)

SELECT o.sfdc_id AS opportunity_id
       , a.id AS account_id
       , s.stage_id AS opportunity_stage_id
       , l.id AS lead_source_id
       , o.weighted_iacv__c AS weighted_iacv
       , COALESCE(o.type, 'Unknown') AS opportunity_type
       , COALESCE(o.sales_segmentation_o__c, 'Unknown') as opportunity_sales_segmentation
       , o.sales_qualified_date__c as sales_qualified_date
       , o.sales_accepted_date__c as sales_accepted_date
       , o.sql_source__c as sales_qualified_source
       , o.closedate AS opportunity_closedate
       , o.created_date AS opportunity_created_date
       , COALESCE(i.product, 'Unknown') as opportunity_product
       , COALESCE(i.period, 'Unknown') as billing_period
       , COALESCE(o.name, 'Unknown') as opportunity_name
       , o.reason_for_loss
       , o.reason_for_loss_details
       , o.ownerid
       , CASE
          WHEN (o.days_in_stage > 30 OR o.over_100k IS TRUE OR o.push_counter__c > 0)
            THEN TRUE
          ELSE FALSE
         END AS is_risky
       , o.days_in_stage
       , o.lastactivitydate
       , o.competitors__C
       , i.qty AS quantity
       , i.iacv
       , i.renewal_acv
       , i.acv
       , i.tcv
       , o.deal_size
       , o.is_won
       , o.upside_iacv
       , o.upside_swing_deal_iacv
       , o.is_swing_deal
       , o.merged_opportunity_id
FROM lineitems i
INNER JOIN opportunity o ON i.opportunity_id=o.sfdc_id
INNER JOIN oppstage s ON o.stagename=s.primary_label
INNER JOIN leadsource l on o.leadsource=l.Initial_Source
INNER JOIN account a on o.accountId=a.sfdc_account_id