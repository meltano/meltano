{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/subsidiary.html
#}



with base as (

		SELECT *
		FROM netsuite.transaction_lines

), renamed as (

		SELECT unique_id as transaction_line_id,
				transaction_id,
				line as transaction_line,
				account_id,
				account_name,
				credit as credit_amount,
				--credit_tax
				debit as debit_amount,
				--debit_tax
				department_id,
				department_name,
				entity_id,
				entity_name,
				memo,
				--amortization_end_date
				--amortization_residual
				--amortization_sched_id
				--amortization_sched_name
				--amortiz_start_date
				--class_id
				--class_name
				--due_to_from_subsidiary_id
				--due_to_from_subsidiary_name
				--eliminate
				--end_date
				gross_amt as gross_amount,
				line_fx_rate as line_exchange_rate,
				line_subsidiary_id,
				line_subsidiary_name
				--line_tax_code_id
				--line_tax_code_name
				--line_tax_rate
				--line_unit_id
				--line_unit_name
				--location_id
				--location_name
				--preview_debit
				--residual
				--revenue_recognition_rule_id
				--revenue_recognition_rule_name
				--schedule_id
				--schedule_name
				--schedule_num_id
				--schedule_num_name
				--start_date
				--tax1_acct_id
				--tax1_acct_name
				--tax1_amt
				--tax_account_id
				--tax_account_name
				--tax_basis
				--tax_code_id
				--tax_code_name
				--tax_rate1
				--total_amount
				--custom_field_list --is json
    FROM base

)

SELECT *
FROM renamed


