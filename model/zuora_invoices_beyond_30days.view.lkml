view: zuora_invoices_beyond_30days {
  sql_table_name: analytics.zuora_invoices_beyond_30days ;;


  dimension: account_name {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.account_name ;;
  }

  dimension: day_range {
    hidden: yes
    type: string
    sql: ${TABLE}.day_range ;;
  }

  dimension: list_of_open_invoices {
    type: string
    sql: ${TABLE}.list_of_open_invoices ;;
  }

#   set: detail {
#     fields: [name, day_range, list_of_open_invoices]
#   }
}
