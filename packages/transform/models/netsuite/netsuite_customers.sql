{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/customer.html
#}

with base as (

		SELECT *
		FROM netsuite.customers

), renamed as (

	SELECT internal_id as customer_id,
		company_name as customer_name,
       	entity_id as entity_name,
       	balance,
       	consol_balance as consolidated_balance,
       	consol_days_overdue as consolidated_balance_days_overdue,
       	overdue_balance
    FROM base

)

SELECT *
FROM renamed





