view: historical_headcount {
  # # You can specify the table name if it's different from the view name:
  sql_table_name: analytics.historical_headcount ;;
  #
  # Define your dimensions and measures here, like this:
  dimension: id {
    type: number
    hidden: yes
    primary_key: yes
    sql: ${TABLE}.prinmary_key ;;
  }

  dimension_group: date {
    type: time
    timeframes: [
      raw,
      date,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.month_of ;;
  }

  dimension: function {
    description: "Function of GitLab"
    type: string
    sql: ${TABLE}.function ;;
  }

  measure: total_employees {
    description: "No. of Employees"
    type: sum
    value_format: "#,##0"
    drill_fields: [function,total_employees]
    sql: ${TABLE}.employee_count ;;
  }
}
