{{
  config({
    "materialized":"table",
  })
}}

with ss_opportunity as (
	  select * from {{ ref('snapshot_opportunity') }}
),

leadsource as (
    select * from {{ ref('dim_leadsource') }}
),

account as (
    select * from {{ ref('dim_account') }}
),

oppstage as (
		select * from {{ ref('dim_opportunitystage') }}

),

curr_snapshot as (
		select * from {{ ref('f_opportunity') }}
)

SELECT o.sfdc_opportunity_id AS opportunity_id
	   , o.snapshot_date AS snapshot_date
       , a.id AS account_id
       , s.stage_id AS opportunity_stage_id
       , l.id AS lead_source_id
       , COALESCE(o.type, 'Unknown') AS opportunity_type
       , COALESCE(o.sales_segmentation_o__c, 'Unknown') as opportunity_sales_segmentation
       , o.sales_qualified_date__c as sales_qualified_date
       , o.sales_accepted_date__c as sales_accepted_date
       , o.sql_source__c as sales_qualified_source
       , o.closedate AS opportunity_closedate
       , COALESCE(o.name, 'Unknown') as opportunity_name
       , o.reason_for_loss
       , o.reason_for_loss_details
       , o.iacv
       , o.Renewal_ACV
       , o.acv
       , o.tcv
       , o.ownerid
FROM  ss_opportunity o 
INNER JOIN oppstage s ON o.stagename=s.primary_label
INNER JOIN leadsource l on o.leadsource=l.Initial_Source
INNER JOIN account a on o.accountId=a.sfdc_account_id


UNION 

-- This gets the opps for the current day b/c there is no snapshot
SELECT opportunity_id,
       CURRENT_TIMESTAMP as snapshot_date,
       account_id,
       opportunity_stage_id,
       lead_source_id,
       opportunity_type,
       opportunity_sales_segmentation,
       sales_qualified_date,
       sales_accepted_date,
       sales_qualified_source,
       opportunity_closedate,
       opportunity_name,
       reason_for_loss,
       reason_for_loss_details,
       SUM(iacv) iacv,
       SUM(renewal_acv) renewal_acv,
       SUM(acv) acv,
       SUM(tcv) tcv,
       ownerid
FROM curr_snapshot
GROUP BY opportunity_id,
         account_id,
         opportunity_stage_id,
         lead_source_id,
         opportunity_type,
         opportunity_sales_segmentation,
         sales_qualified_date,
         sales_accepted_date,
         sales_qualified_source,
         opportunity_closedate,
         opportunity_name,
         reason_for_loss,
         reason_for_loss_details,
         ownerid

