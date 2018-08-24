WITH sfdc_opportunity AS ( 

	SELECT * FROM {{ref('sfdc_opportunity')}}

), sfdc_opportunitystage AS (

   SELECT * FROM {{ref('sfdc_opportunitystage')}}

), lead_source AS (


	SELECT * FROM {{ref('dim_leadsource')}}

), layered AS (

    SELECT
        sfdc_opportunity.*,
        lead_source.id as lead_source_id,
        lead_source.initial_source as lead_source_name,
        lead_source.initial_source_type as lead_source_type,
        sfdc_opportunitystage.is_won AS is_won,
        sfdc_opportunitystage.default_probability as stage_default_probability,
        sfdc_opportunitystage.is_active as stage_is_active,
        sfdc_opportunitystage.is_closed as stage_is_closed,
        sfdc_opportunitystage.stage_state as stage_state,
        sfdc_opportunitystage.mapped_stage as mapped_stage,
        CASE 
          WHEN (sfdc_opportunity.days_in_stage > 30 
          	OR sfdc_opportunity.incremental_acv > 100000 
          	OR sfdc_opportunity.pushed_count > 0)
            THEN TRUE
          ELSE FALSE
         END AS is_risky
    FROM sfdc_opportunity
    INNER JOIN sfdc_opportunitystage on sfdc_opportunity.stage_name = sfdc_opportunitystage.primary_label
    INNER JOIN lead_source on sfdc_opportunity.lead_source = lead_source.Initial_Source

)

SELECT *
FROM layered
