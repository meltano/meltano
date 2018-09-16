WITH source AS (

	SELECT *
	FROM zuora.subscription


), renamed AS(

	SELECT
	    id                                  as subscription_id,
		name                                as subscription_name,
		--keys	
		accountid                           as account_id,
		creatoraccountid                    as creator_account_id,
		creatorinvoiceownerid               as creator_invoice_owner_id,
		invoiceownerid                      as invoice_owner_id,
		opportunityid__c                    as sfdc_opportunity_id,
		originalid                          as original_id,
		previoussubscriptionid              as previous_subscription_id,
		recurlyid__c                        as sfdc_recurly_id,
		cpqbundlejsonid__qt                 as cpq_bundle_json_id,
		
		-- info
		status                              as subscription_status,
		autorenew                           as auto_renew,
		version                             as version,
		termtype                            as term_type,
		notes                               as notes,
		isinvoiceseparate                   as is_invoice_separate,
		currentterm                         as current_term,
		currenttermperiodtype               as current_term_period_type,
		clickthrougheularequired__c         as sfdc_click_through_eula_required,
		endcustomerdetails__c               as sfdc_end_customer_details,

		--key_dates
		cancelleddate                       as cancelled_date,
		contractacceptancedate              as contract_acceptance_date,
		contracteffectivedate               as contract_effective_date,
		initialterm                         as initial_term,
		initialtermperiodtype               as initial_term_period_type,
		termenddate                         as term_end_date,
		termstartdate                       as term_start_date,
		subscriptionenddate                 as subscription_end_date,
		subscriptionstartdate               as subscription_start_date,
		serviceactivationdate               as service_activiation_date,
		opportunityclosedate__qt            as opportunity_close_date,
		originalcreateddate                 as original_created_date,

		--foreign synced info
		opportunityname__qt                 as opportunity_name,
		purchase_order__c                   as sfdc_purchase_order,
		purchaseorder__c                    as sfdc_purchase_order_,
		quotebusinesstype__qt               as quote_business_type,
		quotenumber__qt                     as quote_number,
		quotetype__qt                       as quote_type,

		--renewal info
		renewalsetting                      as renewal_setting,
		renewal_subscription__c__c          as sfdc_renewal_subscription,
		renewalterm                         as renewal_term,
		renewaltermperiodtype               as renewal_term_period_type,
		exclude_from_renewal_report__c__c   as exclude_from_renewal_report,

		--metadata
		updatedbyid                         as updated_by_id,
		updateddate                         as updated_date,
		createdbyid                         as created_by_id,
		createddate                         as created_date


	FROM source
	WHERE (excludefromanalysis__c = FALSE OR excludefromanalysis__c IS NULL)

)

SELECT *
FROM renamed