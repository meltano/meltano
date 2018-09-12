view: zuora_ar {
  sql_table_name: analytics.zuora_accounts_receivables ;;
  label: "Zuora Accounts Receivables"

  #
  dimension: 30_days_open_invoices {
    #hidden: yes
    type:  string
    sql: ${zuora_invoices_beyond_30days.list_of_open_invoices} ;;

  }

  dimension: send_email {
    hidden: yes
    sql: ${account_number} ;;
    html: <a href="https://mail.google.com/mail/?view=cm&fs=1&to={{ email._value }}&cc=ar@gitlab.com&su={{customer._value}} invoice(s) are overdue&body=Hi {{owner._value}},
                   %0D%0DI am reaching out to let you know that the GitLab invoice(s) below are 30 days overdue.
                   %0D%0DThe current balance of the invoice(s) amount to {{balance_sum._rendered_value}}.
                   %0D%0DIf you have not already done so, please take a moment to make the payment today.
                   %0D%0DThe invoice can be paid via wire transfer or credit card.
                   %0D%0DWe look forward to receiving your payment.
                   %0D%0D{{30_days_open_invoices._value}}
                   %0D%0DThank you," target="_blank">
          <img src="https://upload.wikimedia.org/wikipedia/commons/4/4e/Gmail_Icon.png" width="16" height="16"/>
          <a> Click icon to email
          ;;
  }
  #
  dimension: entity {
    description: "GitLab Entity"
    type: string
    sql: ${TABLE}.entity ;;
  }
  #
  dimension: email {
    description: "Customer Email"
    type: string
    sql: ${TABLE}.email ;;
  }
  #
  dimension: day_range {
    description: "Account Number of Zuora Customer"
    type: string
    sql: ${TABLE}.range_since_due_date ;;
  }
  #
  dimension: invoice {
    description: "Invoice of Customer"
    type: string
    sql: ${TABLE}.invoice ;;
  }
  #
  dimension: customer {
    description: "Customer"
    type: string
    #drill_fields: [drill_1*]
    sql: ${TABLE}.account_name ;;
  }
  #
  dimension: currency {
    description: "Currency of Customer"
    type: string
    sql: ${TABLE}.currency ;;
  }
  #
  dimension: account_number {
    description: "Acct # of Customer"
    type: string
    sql: ${TABLE}.account_number ;;
  }
  #
  dimension: invoice_status {
    description: "Invoice Status"
    type: string
    sql: ${TABLE}.invoice_status ;;
  }
  #
  dimension: duedate {
    description: "Due Date of Invoice"
    type: string
    sql: ${TABLE}.due_date ;;
  }
  #
  dimension: owner {
    description: "Customer Name"
    type: string
    sql: ${TABLE}.owner ;;
  }
  #
  dimension: balance {
    description: "Balance due from Customer"
    type: number
    sql: ${TABLE}.balance ;;
    drill_fields: [entity,customer,account_number,30_days_open_invoices,send_email]
  }
  #
  measure: balance_sum {
    description: "Sum of Balance due from Customer"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.balance ;;
    drill_fields: [entity,customer,account_number,30_days_open_invoices,send_email,balance_sum]
  }
  #
  measure: invoice_cnt {
    description: "Count from Customer"
    type: count_distinct
    drill_fields: [entity,customer,account_number,duedate,balance]
    sql: ${TABLE}.invoice ;;
  }

  measure: count {
    type: count
  }

}
