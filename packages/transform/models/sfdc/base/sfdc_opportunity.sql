WITH source AS ( 

	SELECT *
	FROM sfdc.opportunity
 
),

    renamed AS(

	SELECT 
		id as opportunity_id, 
		name as opportunity_name,
		
		-- keys
		accountid as account_id,
		ownerid as owner_id,

		-- logistical info

		opportunity_owner__c as owner,
		engagement_type__c as sales_path,
		sql_source__c as generated_source,
		COALESCE((initcap(sales_segmentation_o__c)), 'Unknown') as sales_segment,
		(initcap(ultimate_parent_sales_segment_o__c)) as parent_segment,
		type as sales_type,
		closedate as close_date,
		createddate as created_date,
		stagename as stage_name,
		products_purchased__c as product,
		current_date - greatest(
		      x0_pending_acceptance_date__c,
		      x1_discovery_date__c,
		      x2_scoping_date__c,
		      x3_technical_evaluation_date__c,
		      x4_proposal_date__c,
		      x5_negotiating_date__c,
		      x6_closed_won_date__c,
		      x7_closed_lost_date__c,
		      x8_unqualified_date__c
		  ) :: DATE + 1  AS days_in_stage,
		sales_accepted_date__c as sales_accepted_date,
		sales_qualified_date__c as sales_qualified_date,
		merged_opportunity__c as merged_opportunity_id,

		-- opp info
		acv_2__c as acv,
		sql_source__c as sales_qualified_source,
		-- Should confirm which IACV is which
		incremental_acv_2__c as forecasted_iacv,
		incremental_acv__c as incremental_acv,
		renewal_amount__c as renewal_amount,
		renewal_acv__c as renewal_acv,
		nrv__c as nrv,
		sales_segmentation_o__c as segment,
		amount as total_contract_value,
		leadsource as lead_source,
		products_purchased__c AS products_purchased,
		competitors__C as competitors,
		reason_for_lost__c as reason_for_loss,
        reason_for_lost_details__c as reason_for_loss_details,
        push_counter__c as pushed_count,
        upside_iacv__c as upside_iacv,
        upside_swing_deal_iacv__c as upside_swing_deal_iacv,
        swing_deal__c as is_swing_deal,
		CASE WHEN
            incremental_acv_2__c :: DECIMAL < 5000
            THEN '1 - Small (<5k)'
          WHEN incremental_acv_2__c :: DECIMAL >= 5000 AND incremental_acv_2__c :: DECIMAL < 25000
            THEN '2 - Medium (5k - 25k)'
          WHEN incremental_acv_2__c :: DECIMAL >= 25000 AND incremental_acv_2__c :: DECIMAL < 100000
            THEN '3 - Big (25k - 100k)'
          WHEN incremental_acv_2__c :: DECIMAL >= 100000
            THEN '4 - Jumbo (>100k)'
          ELSE '5 - Unknown' END AS deal_size,
		
		
		CASE WHEN acv_2__c >= 0 THEN 1
             ELSE 0
        	END AS closed_deals,  -- so that you can exclude closed deals that had negative impact

		-- metadata
		isdeleted as is_deleted,
		lastactivitydate as last_activity_date,
		date_part('day', now() - lastactivitydate) as days_since_last_activity


	FROM source
	WHERE accountid IS NOT NULL
	AND isdeleted = FALSE

)

SELECT *
FROM renamed
