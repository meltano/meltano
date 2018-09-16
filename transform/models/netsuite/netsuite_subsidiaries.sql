{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/subsidiary.html
#}



with base as (

		SELECT *
		FROM netsuite.subsidiaries

), renamed as (

		SELECT internal_id as subsidiary_id,
           name as subsidiary_name,
           currency,
           country
    FROM base

)

SELECT *
FROM renamed



