WITH source AS (

	SELECT *
	FROM sfdc.contact

), renamed AS(

	SELECT
		-- id
		id as contact_id,
		name as contact_name,

		-- keys
		accountid as account_id,
		masterrecordid as master_record_id,
		ownerid as owner_id,
		recordtypeid as record_type_id,
		reportstoid as reports_to_id, 

		--contact info
		
		title as contact_title,
		role__c as contact_role,
		mobilephone as mobile_phone,
		person_score__c as person_score,

		department as department,
		contact_status__c as contact_status,
		requested_contact__c as requested_contact,
		inactive_contact__c as inactive_contact,
		hasoptedoutofemail as has_opted_out_email,
		invalid_email_address__c as invalid_email_address,
		isemailbounced as email_is_bounced,
		emailbounceddate as email_bounced_date,
		emailbouncedreason as email_bounced_reason,

		data_quality_score__c as data_quality_score,
		data_quality_description__c as data_quality_description,

		mailingstreet as mailing_address,
		mailingcity as mailing_city,
		mailingstate as mailing_state,
		mailingstatecode as mailing_state_code,
		mailingcountry as mailing_country,
		mailingcountrycode as mailing_country_code,
		mailingpostalcode as mailing_zip_code,

		-- info
		using_ce__c as using_ce,
		ee_trial_start_date__c as ee_trial_start_date,
		ee_trial_end_date__c as ee_trial_end_date,
		industry__c as industry,
		responded_to_githost_price_change__c as responded_to_githost_price_change, -- maybe we can exclude this if it's not relevant
		leadsource as lead_source,
		lead_source_type__c as lead_source_type,
		outreach_stage__c as outreach_stage,
		account_type__c as account_type,

		--gl info
		account_owner__c as account_owner,
		ae_comments__c as ae_comments,
		business_development_rep__c as business_development_rep_name,
		outbound_bdr__c as outbound_business_development_rep_name,

		-- metadata
		createdbyid as created_by_id,
		createddate as created_date,
		lastreferenceddate as last_referenced_date,
		lastactivitydate as last_activity_date,
		lastcurequestdate as last_cu_request_date,
		lastcuupdatedate as last_cu_update_date,
		lastvieweddate as last_viewed_date,
		lastmodifiedbyid as last_modified_by_id,
		lastmodifieddate as last_modified_date,
		systemmodstamp


	FROM source
	WHERE isdeleted IS FALSE

)

SELECT *
FROM renamed





------excluded

---- infer
--infer__infer_band__c as ,
--infer__infer_hash__c as ,
--infer__infer_last_modified__c as ,
--infer__infer_rating__c as ,
--infer__infer_score__c as ,

---- lean data
--leandata__ld_segment__c as ,
--leandata__matched_buyer_persona__c as ,
--leandata__modified_score__c as ,
--leandata__routing_action__c as ,
--leandata__tag__c as ,

----marketo
--mkto_si__add_to_marketo_campaign__c as ,
--mkto_si__hidedate__c as ,
--mkto_si__last_interesting_moment__c as ,
--mkto_si__last_interesting_moment_date__c as ,
--mkto_si__last_interesting_moment_desc__c as ,
--mkto_si__last_interesting_moment_source__c as ,
--mkto_si__last_interesting_moment_type__c as ,
--mkto_si__mkto_lead_score__c as ,
--mkto_si__priority__c as ,
--mkto_si__relative_score__c as ,
--mkto_si__relative_score_value__c as ,
--mkto_si__sales_insight__c as ,
--mkto_si__urgency__c as ,
--mkto_si__urgency_value__c as ,
--mkto_si__view_in_marketo__c as ,
--mkto71_acquisition_date__c as ,
--mkto71_acquisition_program__c as ,
--mkto71_acquisition_program_id__c as ,
--mkto71_inferred_city__c as ,
--mkto71_inferred_company__c as ,
--mkto71_inferred_country__c as ,
--mkto71_inferred_metropolitan_area__c as ,
--mkto71_inferred_phone_area_code__c as ,
--mkto71_inferred_postal_code__c as ,
--mkto71_inferred_state_region__c as ,
--mkto71_lead_score__c as ,
--mkto71_original_referrer__c as ,
--mkto71_original_search_engine__c as ,
--mkto71_original_search_phrase__c as ,
--mkto71_original_source_info__c as ,
--mkto71_original_source_type__c as ,

----zendesk
--zendesk__create_in_zendesk__c as ,
