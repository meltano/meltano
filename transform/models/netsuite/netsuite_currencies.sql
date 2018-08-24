{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/currency.html
#}

with base as (
	
		SELECT *
		FROM netsuite.currencies

), renamed as (

		SELECT internal_id as currency_id,
          name as currency_name,
          symbol as currency_symbol,
          exchange_rate --to the US Dollar
		FROM base

)

SELECT *
FROM renamed


