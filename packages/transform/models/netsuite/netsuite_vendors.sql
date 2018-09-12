{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/vendor.html
#}

with base as (

		SELECT *
		FROM netsuite.vendors

), renamed as (

		SELECT internal_id as internal_vendor_id,
				account_number as account_number,
				--alt_email
				--alt_name
				--alt_phone
				--balance
				balance_primary as vendor_balance, --vendor's current accounts payable balance
				--bcn
				--bill_pay
				comments as vendor_comments,
				company_name as vendor_name, -- reimbursements sometimes list an employee as the vendor
				--credit_limit
				default_address as vendor_address,
				--eligible_for_commission
				--email  --only used for gitlab employees
				--email_transactions
				entity_id as entity_name,
				--fax
				--fax_transactions
				--first_name
				--give_access
				--home_phone
				is1099_eligible as is_1099_eligible,
				is_accountant as is_accountant,
				is_inactive as is_inactive,
				--is_job_resource_vend as is_job_resource_vendor
				is_person,
				--labor_cost
				--last_name
				CASE WHEN lower(legal_name) LIKE '%gitlab.com%'
									THEN (first_name || ' ' || last_name)
							 ELSE legal_name
							 END AS legal_name --legal name is email addresses for gitlabbers
				--middle_name
				--mobile_phone
				--opening_balance
				--password
				--password2
				--phone
				--phonetic_name
				--print_on_check_as
				--print_transactions
				--purchase_order_amount
				--purchase_order_quantity
				--purchase_order_quantity_diff
				--receipt_amount
				--receipt_quantity
				--receipt_quantity_diff
				--require_pwd_change
				--salutation
				--send_email
				--tax_id_num
				--title
				--unbilled_orders
				--unbilled_orders_primary
				--url
				--vat_reg_number

		FROM base

)

SELECT *
FROM renamed


