WITH source AS (

	SELECT *
	FROM sfdc.campaign

), renamed AS(

	SELECT
		id as campaign_id,
		name as campaign_name,
		isactive as is_active,
		startdate as start_date,
		enddate as end_date,
		status as status,
		type as type,

		--keys
		campaignmemberrecordtypeid as campaign_member_record_type_id,
		ownerid as campaign_owner_id,
		parentid as campaign_parent_id,

		--info
		data_quality_description__c as data_quality_description,
		data_quality_score__c as data_quality_score,
		description as description,

		--projections
		budgetedcost as budgeted_cost,
		expectedresponse as expected_response,
		expectedrevenue as expected_revenue,

		--results
		actualcost as actual_cost,
		amountallopportunities as amount_all_opportunities,
		amountwonopportunities as amount_won_opportunities,
		numberofcontacts as count_contacts,
		numberofconvertedleads as count_converted_leads,
		numberofleads as count_leads,
		numberofopportunities as count_opportunities,
		numberofresponses as count_responses,
		numberofwonopportunities as count_won_opportunities,
		numbersent as count_sent,


		--metadata
		createddate as created_date,
		createdbyid as created_by_id,
		lastmodifiedbyid as last_modified_by_id,
		lastmodifieddate as last_modified_date,
		lastreferenceddate as last_referenced_date,
		lastvieweddate as last_viewed_date,
		lastactivitydate as last_activity_date,
		systemmodstamp

	FROM source
	WHERE isdeleted IS FALSE

)

SELECT *
FROM renamed


--- excluded columns
--lean data:

--leandata__back_dated__c as ,
--leandata__rep_lt_attribution__c as ,
--leandata__rep_lt_bookings_attribution__c as ,
--leandata__rep_lt_generated_attribution__c as ,
--leandata__rep_lt_generated_bookings_attribution__c as ,
--leandata__rep_mt_accelerated_attribution__c as ,
--leandata__rep_mt_accelerated_bookings_attr__c as ,
--leandata__rep_mt_generated_attribution__c as ,
--leandata__rep_mt_generated_bookings_attribution__c as ,
--leandata__reporting_average_days_to_close__c as ,
--leandata__reporting_bookings_attribution__c as ,
--leandata__reporting_campaign_member_totals__c as ,
--leandata__reporting_cost__c as ,
--leandata__reporting_ft_attribution_amount__c as ,
--leandata__reporting_ft_bookings_attribution__c as ,
--leandata__reporting_lift__c as ,
--leandata__reporting_mt_attribution_amount__c as ,
--leandata__reporting_num_target_campaign_members__c as ,
--leandata__reporting_number_of_campaign_members__c as ,
--leandata__reporting_number_of_opportunities__c as ,
--leandata__reporting_number_of_touches__c as ,
--leandata__reporting_on_target__c as ,
--leandata__reporting_opportunity_close_rate__c as ,