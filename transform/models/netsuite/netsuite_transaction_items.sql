with base as (

    SELECT *
    FROM netsuite.transaction_items

), renamed as (

    SELECT unique_id as transaction_item_id,
          transaction_id,
          line as transaction_line,
          item_id,
          item_name,
          amount,
          --amount_ordered --not used
          --gross_amt -- not used
          quantity as item_quantity,
          description as transaction_line_description,
          rate as item_rate
          ---- THE REST ARE ALL NO
          --alt_sales_amt
          --bin_numbers
          --catch_up_period_id
          --catch_up_period_name
          --charges_list --is type json but it all null
          --charge_type_id
          --charge_type_name
         -- class_id
          --class_name
          --cost_estimate
          --cost_estimate_type
          --current_percent
          --customer_id
          --customer_name
          --defer_rev_rec
          --department_id
          --department_name
          --exclude_from_rate_request
          --expand_item_group
          --expected_ship_date
          --expiration_date
          --from_job
          --gift_cert_from
          --gift_cert_message
          --gift_cert_number
          --gift_cert_recipient_email
          --gift_cert_recipient_name
          --is_billable
          --is_estimate
          --is_taxable
          --item_is_fulfilled
          --job_id
          --job_name
          --license_code
          --location_id
          --location_name
          --order_line
          --percent_complete
          --price_id
          --price_name
          --quantity_available
          --quantity_fulfilled
          --quantity_on_hand
          --quantity_ordered
          --quantity_remaining

          --rev_rec_end_date
          --rev_rec_schedule_id
          --rev_rec_schedule_name
          --rev_rec_start_date
          --rev_rec_term_in_months
          --serial_numbers
          --ship_address_id
          --ship_address_name
          --ship_carrier
          --ship_group
          --ship_method_id
          --ship_method_name
          --subscription_id
          --subscription_name
          --subscription_line_id
          --subscription_line_name
          --tax1_amt
          --tax_amount
          --tax_code_id
          --tax_code_name
          --tax_details_reference
          --tax_rate1
          --tax_rate2
          --units_id
          --units_name
          --vendor_name
          --vsoe_allocation
          --vsoe_amount
          --vsoe_deferral
          --vsoe_delivered
          --vsoe_is_estimate
          --vsoe_permit_discount
          --vsoe_price
          --vsoe_sop_group
          --amortization_end_date
          --amortization_residual
          --amortization_sched_id
          --amortization_sched_name
          --amortiz_start_date
          --billreceipts_list
          --bill_variance_status
          --landed_cost_category_id
          --landed_cost_category_name
          --order_doc
          --created_from_id
          --created_from_name
          --expected_receipt_date
          --is_closed
          --linked_order_list
          --match_bill_to_receipt
          --purchase_contract_id
          --purchase_contract_name
          --quantity_billed
          --quantity_on_shipments
          --quantity_received
          --options
          --custom_field_list
    FROM base

)

SELECT *
FROM renamed



