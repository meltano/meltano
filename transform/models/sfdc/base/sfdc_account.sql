WITH source AS (

	SELECT *
	FROM sfdc.account

), renamed AS(

	SELECT 
		id                      as account_id,
		name                    as account_name,
		-- keys
		account_id_18__c as account_id_18,
		masterrecordid as master_record_id,
		ownerid as owner_id,
		parentid as parent_id,
		primary_contact_id__c as primary_contact_id,
		recordtypeid as record_type_id,
		ultimate_parent_account_id__c as utimate_parent_id,
		partner_vat_tax_id__c as partner_vat_tax_id,

		-- key people GL side
		entity__c as gitlab_entity,
		federal_account__c as federal_account, --boolean
		gitlab_com_user__c as gitlab_com_user, --boolean
		account_manager__c as account_manager,
		--account_manager_account_team__c as account_manager_account_team ## Why are these all null?
		--account_manager_lu__c
		account_owner_calc__c as account_owner,
		-- account_owner_manager_email__c as account_owner_manager,
		account_owner_team__c as account_owner_team,
		business_development_rep__c as business_development_rep,
		business_development_rep_account_team__c as business_development_rep_team,
		dedicated_service_engineer__c as dedicated_service_engineer,
		sdr__c as sales_development_rep,
		sdr_account_team__c as sales_development_rep_team,
		solutions_architect__c as solutions_architect,
		technical_account_manager_lu__c as technical_account_manager_id, -- lookup on user

		--key people outside
		-- bill_to_email__c as bill_to_email,


		-- info
		{{this.schema}}.id15to18(
              substring(
                  regexp_replace(ultimate_parent_account__c,
                                '_HL_ENCODED_/|<a\s+href="/', '')
                  , 1
                  , 15)
          )                     as ultimate_parent_account_id,
		type as account_type,
		industry,
		product_category__c as product_category,
		customer_since__c::date as customer_since_date,
		sales_segmentation_new__c as new_account_segment,
		sales_segmentation__c as account_segment, -- I would this be called account_segment or sales_segment, but I think this is a breaking change

		--present state info
		health__c as health_score,
		health_score_reasons__c as health_score_explained,


		-- opportunity metrics
		count_of_active_subscription_charges__c as count_active_subscription_charges,
		count_of_active_subscriptions__c as count_active_subscriptions,
		count_of_billing_accounts__c as count_billing_accounts,
		count_of_new_business_won_opps__c as count_of_new_business_won_opportunities,
		count_of_open_renewal_opportunities__c as count_open_renewal_opportunities,
		count_of_opportunities__c as count_opportunities,
		count_of_products_purchased__c as count_products_purchased,
		count_of_won_opportunities__c as count_won_opportunities,
		concurrent_ee_subscriptions__c as count_concurrent_ee_subscriptions,
		ce_instances__c as count_ce_instances,
		active_ce_users__c as count_active_ce_users,
		number_of_open_opportunities__c                 as count_open_opportunities,
		using_ce__c as count_using_ce,


		-- metadata
		createdbyid as created_by_id,
		createddate as created_date,
		isdeleted as is_deleted,
		lastmodifiedbyid as last_modified_by_id,
		lastmodifieddate as last_modified_date,
		lastactivitydate AS last_activity_date,
		lastreferenceddate as last_referenced_date,
		lastvieweddate as last_viewed_date,
		systemmodstamp


	FROM source
	WHERE id IS NOT NULL
	AND isdeleted = FALSE

)

SELECT *
FROM renamed

--List of excluded columns
		--billing info
		--billingstreet as billing_street,
		--billingcity as billing_city,
		--billingstate as billing_state,
		--billingstatecode as billing_state_code,
		--billingcountry as billing_country,
		--billingcountrycode as billing_country_code
		--billingpostalcode as billing_postal_code,
		--billinglongitude as billing_longitude,
		--billinglatitude as billing_latitude,

		--shippingstreet as shipping_street,
		--shippingcity as shipping_city,
		--shippingstate as shipping_state,
		--shippingstatecode as shipping_state_code,
		--shippingcountry as shipping_country,
		--shippingcountrycode as shipping_country_code,
		--shippingpostalcode as shipping_postal_code,
		--shippinglongitude as shipping_longitude,
		--shippinglatitude as shipping_latitude,
		--shippingcountrycode__c as shipping_country_code,

-- all blanks

----- infers 
--infer__infer_band__c
--infer__infer_hash__c
--infer__infer_last_modified__c
--infer__infer_rating__c
--infer__infer_score__c


----- zuora & zendesk
--zendesk__create_in_zendesk__c
--zendesk__createdupdatedflag__c
--zendesk__domain_mapping__c
--zendesk__last_sync_date__c
--zendesk__last_sync_status__c
--zendesk__notes__c
--zendesk__result__c
--zendesk__tags__c
--zendesk__zendesk_oldtags__c
--zendesk__zendesk_organization__c
--zendesk__zendesk_organization_id__c
--zendesk__zendesk_outofsync__c
--zuora__active__c
--zuora__customerpriority__c
--zuora__numberoflocations__c
--zuora__sla__c
--zuora__slaexpirationdate__c
--zuora__slaserialnumber__c
--zuora__upsellopportunity__c
--zuora_issue__c






----- other columns
--absd_campaign__c
--account_initial_start_date__c
--account_tier__c
--ae_comments__c
--carr_all_child_accounts__c
--carr_this_account__c
--carr_total__c
--cmrr_all_child_accounts__c
--cmrr_this_account__c
--cmrr_total__c
--company_technologies__c --notes about existing tech
--data_quality_description__c
--data_quality_score__c
--days_outstanding__c
--description -- text field
--domains__c -- inconsistent structure, some have multiple separated by commas
--dscorgpkg__fortune_rank__c
--dscorgpkg__it_employees__c
--gitlab_team__c --all blanks
--historical_max_users__c --not really used
--initial_start_date__c
--invoice_owner__c
--iseebasiccustomer__c
--iseepluscustomer__c
--iseestandardcustomer__c
--isfilelockingcustomer__c
--isgithostbusinesscustomer__c
--isgithostdevelopercustomer__c
--isgithoststartupcustomer__c
--isgithoststoragecustomer__c
--isgitlabeecustomer__c
--isgitlabgeocustomer__c
--isimplementationsupportcustomer__c
--ispartner
--ispremiumsupportcustomer__c
--it_tedd__c
--large_account__c
--license_user_count__c
--license_utilization__c
--manual_support_upgrade__c
--most_recent_expired_subscription_date__c
--next_invoice_due_date__c
--next_renewal_date__c
--number_of_licenses_all_child_accounts__c
--number_of_licenses_this_account__c
--number_of_licenses_total__c
--numberofemployees
--of_carr__c
--of_licenses__c
--oldest_outstanding_invoice_date__c
--opt_out_file_locking__c
--opt_out_geo__c
--partner_account_iban_number__c
--partner_bank_address__c
--partner_bank_name__c
--partner_beneficiary_name__c
--partner_name_and_type__c
--partner_routing__c
--paymenttermnumeric__c
--phone
--photourl
--potential_carr_this_account__c
--potential_ee_subscription_amount__c
--potential_ee_users_total__c
--potential_users__c
--potential_users_all_child_accounts__c
--previous_account_name__c
--previous_account_owner__c
--primary_contact__c
--primary_contact_email__c
--primary_contact_first_name__c
--primary_contact_last_name__c
--products_purchased__c
--reference_type__c
--referenceable_customer__c
--referenceable_customer_notes__c
--region__c
--reseller__c
--reseller_discount__c
--reseller_type__c
--revenue__c
--special_terms__c
--sub_industry__c
--sub_region__c
--subscription_amount__c
--sum_of_open_renewal_opportunities__c
--support_level__c
--support_level_new__c
--support_level_numeric__c
--technology_stack__c
--tedd_employees__c
--temp_duplicated_account__c
--terminus_clicks__c
--terminus_impressions__c
--terminus_spend__c
--terminus_velocity_level__c
--territories_covered__c
--territory__c
--top_list__c
--total_invoiced__c
--total_invoiced_outstanding__c
--total_invoiced_paid__c
--trigger_workflow__c
--type_amount_close_date__c
--ultimate_parent__c
--website



