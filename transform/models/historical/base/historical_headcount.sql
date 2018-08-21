WITH source AS (

	SELECT *
	FROM historical.headcount

), renamed AS (


	SELECT uniquekey::integer as primary_key,
			month::date as month_of,
			function as function,
			employee_cnt::integer as employee_count,
			
			--metadata
			TIMESTAMP 'epoch' + updated_at * INTERVAL '1 second' as updated_at
			
	FROM source

)

SELECT *
FROM renamed