WITH source AS (

	SELECT *
	FROM zuora.account

), renamed AS(

	SELECT 
		id                              as account_id,
		-- keys
		communicationprofileid          as communication_profile_id,
		{{this.schema}}.id15to18(crmid) as crm_id,
		defaultpaymentmethodid          as default_payment_method_id,
		invoicetemplateid               as invoice_template_id,
		parentid                        as parent_id,
		soldtocontactid                 as sold_to_contact_id,
		billtocontactid                 as bill_to_contact_id,
		taxexemptcertificateid          as tax_exempt_certificate_id,
		taxexemptcertificatetype        as tax_exempt_certificate_type,

		-- account info
		accountnumber                   as account_number,
		name                            as account_name,
		notes                           as account_notes,
		purchaseordernumber             as purchase_order_number,
		accountcode__c                  as sfdc_account_code,
		status, 
		entity__c                       as sfdc_entity,

		autopay                         as auto_pay,
		balance                         as balance,
		creditbalance                   as credit_balance,
		billcycleday                    as bill_cycle_day,
		currency                        as currency,
		conversionrate__c               as sfdc_conversion_rate,
		paymentterm                     as payment_term,

		allowinvoiceedit                as allow_invoice_edit,
		batch,
		invoicedeliveryprefsemail       as invoice_delivery_prefs_email,
		invoicedeliveryprefsprint       as invoice_delivery_prefs_print,
		paymentgateway                  as payment_gateway,

		customerservicerepname          as customer_service_rep_name,
		salesrepname                    as sales_rep_name,
		additionalemailaddresses        as additional_email_addresses,
		billtocontact                   as bill_to_contact,
		parent__c                       as sfdc_parent,


		-- financial info
		lastinvoicedate                 as last_invoice_date,

		-- metadata
		createdbyid                     as created_by_id,
		createddate                     as created_date,
		updatedbyid                     as updated_by_id,
		updateddate                     as updated_date


	FROM source
	WHERE id not in
	-- Removes test accounts from Zuora
	    (
	        '2c92a008643512650164430b9c562527', -- WILSON GMBH TEST ACCOUNT
	        '2c92a0fc60202e4a0160503669826d14', -- Test Account
	        '2c92a0fd62b7fe7e0162d6e7993c2341', -- Test Estuate Account
	        '2c92a0ff5e09bd63015e0f4d01616d0d', -- Test Zuora Account
	        '2c92a0ff5e09bd69015e0f42f8c97cc9', -- Test Account Invoice Owner
	        '2c92a0fc5f33da20015f43ee78875ec2', -- Wilson Test
	        '2c92a0ff6446d76201644739829d1e33', -- Test DE
	        '2c92a0ff605102760160529eb44f287e', -- Wilson TEST
	        '2c92a0fd55767b97015579b5185d2a6e', -- Payment Gateway Testing
	        '2c92a0fe6477df2e0164888d62fc5628'  -- Timostestcompany
	    )

)

SELECT *
FROM renamed