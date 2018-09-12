view: zuora_account {
  sql_table_name: zuora.account ;;
  #
  # # Define your dimensions and measures here, like this:
  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  #
  dimension: account_name {
    description: "Name of Zuora Customer"
    type: string
    sql: ${TABLE}.name ;;
  }
  #
  dimension: account_number {
    description: "Account Number of Zuora Customer"
    type: string
    sql: ${TABLE}.accountnumber ;;
  }
  #
  dimension: currency {
    description: "Currency of Zuora Customer"
    type: string
    sql: ${TABLE}.currency ;;
  }
}
