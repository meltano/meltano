WITH source AS (

	SELECT *
	FROM sfdc.opportunitylineitem

), renamed AS(

	SELECT

		--id
		id as opportunity_line_item_id,
		name as opportunity_line_item_name,
		description as opportunity_line_item_description,

		--keys
		opportunityid as opportunity_id,
		pricebookentryid as price_book_entry_id,
		product2id as product_id,
		opportunity_product_id__c as opportunity_product_id,

		--info
		product_code_from_products__c as product_code_from_products,
		product_name_from_products__c as product_name_from_products,
		listprice as list_price,
		productcode as product_code,
		quantity as quantity,
		servicedate as service_date,
		sortorder as sort_order,
		ticket_group_numeric__c as ticket_group_numeric,
		totalprice as total_price,
		unitprice as unit_price,

		--metadata
		createdbyid as created_by_id,
		createddate as created_date,
		lastmodifiedbyid as last_modified_id,
		lastmodifieddate as last_modified_date,
		systemmodstamp


	FROM source

)

SELECT *
FROM renamed