view: zuora_current_arr {
  sql_table_name: analytics.zuora_current_arr ;;
  label: "Zuora Current ARR"
  #
  measure: over_0 {
    description: "Over 0 Customers"
    type: number
    value_format: "#,##0"
    sql: ${TABLE}.over_0 ;;
  }
  #
  measure: over_5k {
    description: "Over 5K Customers"
    type: number
    value_format: "#,##0"
    sql: ${TABLE}.over_5k ;;
  }
  #
  measure: over_50k {
    description: "Over 50K Customers"
    type: number
    value_format: "#,##0"
    sql: ${TABLE}.over_50k ;;
  }
  #
  measure: over_100k {
    description: "Over 100K Customers"
    type: number
    value_format: "#,##0"
    sql: ${TABLE}.over_100k ;;
  }
  #
  measure: current_arr {
    description: "Current ARR"
    type: number
    value_format: "$#,##0"
    sql: ${TABLE}.current_arr ;;
  }

}
