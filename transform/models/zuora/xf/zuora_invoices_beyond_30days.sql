WITH zuora_invoice as (

  SELECT * FROM {{ref('zuora_invoice')}}

), zuora_account as (

  SELECT * FROM {{ref('zuora_account')}}

), open_invoices as (

  SELECT zuora_account.account_name,
       CASE
          WHEN (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) < 30 THEN '1: <30'
          WHEN (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) >= 30 
            AND (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) <= 60 THEN '2: 30-60'
          WHEN (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) >= 61 
            AND (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) <= 90 THEN '3: 61-90'
          WHEN (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) >= 91 THEN '4: >90'
          ELSE 'Unknown'
        END AS day_range,
        STRING_AGG(zuora_invoice.invoice_number, ', ') 
          OVER (partition by zuora_account.account_name) as open_invoices
  FROM zuora_invoice
  INNER JOIN zuora_account
    ON zuora_invoice.account_id = zuora_account.account_id
  WHERE (EXTRACT(DAY FROM zuora_invoice.due_date - CURRENT_DATE)*-1) >= 31

)

SELECT account_name,
        day_range,
        max(open_invoices) as list_of_open_invoices 
FROM open_invoices
GROUP BY 1, 2
