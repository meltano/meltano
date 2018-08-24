WITH source AS (

	SELECT *
	FROM zuora.contact

), renamed AS(

	SELECT 
		id as contact_id,
		-- keys
		accountid as account_id,


		-- contact info
		firstname as first_name,
		lastname as last_name,
		nickname,
		address1 as street_address,
		address2 as street_address2,
		county,
		state,
		postalcode as postal_code,
		city,
		country,
		taxregion as tax_region,
		workemail as work_email,
		workphone as work_phone,
		otherphone as other_phone,
		otherphonetype as other_phone_type,
		fax,
		homephone as home_phone,
		mobilephone as mobile_phone,
		personalemail as personal_email,
		description,


		-- metadata
		createdbyid as created_by_id,
		createddate as created_date,
		updatedbyid as updated_by_id,
		updateddate as updated_date

	FROM source

)

SELECT *
FROM renamed