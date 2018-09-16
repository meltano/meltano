WITH source AS (

	SELECT *
	FROM zuora.invoice

), renamed AS(

	SELECT 
		id as invoice_id,
		-- keys
		accountid as account_id,

		-- invoice metadata
		duedate as due_date,
		invoicenumber as invoice_number,
		invoicedate as invoice_date,
		status as status,

		lastemailsentdate as last_email_sent_date,
		posteddate as posted_date,
		targetdate as target_date,


		includesonetime as includes_one_time,
		includesrecurring as includesrecurring,
		includesusage as includes_usage,
		transferredtoaccounting as transferred_to_accounting,

		-- financial info
		adjustmentamount as adjustment_amount,
		amount,
		amountwithouttax as amount_without_tax, 
		balance,
		creditbalanceadjustmentamount as credit_balance_adjustment_amount,
		paymentamount as payment_amount,
		refundamount as refund_amount,
		taxamount as tax_amount,
		taxexemptamount as tax_exempt_amount,
		comments,

		-- ext1, ext2, ext3, ... ext9

		-- metadata
		createdbyid as created_by_id,
		createddate as created_date,
		postedby as posted_by,
		source as source,
		source as source_id,
		updatedbyid as updated_by_id,
		updateddate as updated_date

	FROM source

)

SELECT *
FROM renamed