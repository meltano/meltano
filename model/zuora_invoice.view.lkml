view: zuora_invoice {
  sql_table_name: zuora.invoice ;;
  #
  # # Define your dimensions and measures here, like this:
  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  #
  dimension: accountid {
    hidden: yes
    type: string
    sql: ${TABLE}.accountid ;;
  }
  #
  dimension: duedate {
    description: "Invoice Due Date"
    type: date
    sql: ${TABLE}.duedate ;;
  }
  #
  dimension: status {
    description: "Invoice Status"
    type: string
    sql: ${TABLE}.status ;;
  }
  #
  dimension: invoicenumber {
    description: "Invoice Number"
    type: string
    sql: ${TABLE}.invoicenumber ;;
  }
  #
  dimension: days_overdue {
    description: "Days Overdue on Invoice"
    type: number
    sql: EXTRACT(DAY FROM ${TABLE}.duedate - CURRENT_DATE)*-1 ;;
  }
  #
  dimension: day_range {
    label: "Days Range Outstanding"
    case: {
      when: {
        sql: ${days_overdue} <30 ;;
        label: "<30"
      }
      when: {
        sql: ${days_overdue} >= 30 AND ${days_overdue} <=60 ;;
        label: "30-60"
      }
      when: {
        sql:  ${days_overdue} >= 61 AND ${days_overdue} <=90  ;;
        label: "61-90"
      }
      when: {
        sql:  ${days_overdue} >= 91  ;;
        label: ">90"
      }
      # possibly more when statements
      else: "Unknown"
    }
  }
  #
  measure: balance {
    description: "Balance due from Customer"
    type: sum
    sql: ${TABLE}.balance ;;
  }
  #
  measure: invoice {
    description: "Count Distinct Invoices"
    type: count_distinct
    sql: ${TABLE}.invoicenumber ;;
  }
}
