view: historical_sales_quota {
  sql_table_name: analytics.historical_sales_quota ;;

  dimension: account_owner {
    type: string
    sql: ${TABLE}.account_owner ;;
  }

  dimension_group: adjusted_start_date {
    type: time
    timeframes: [
      date,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.adjusted_start_date::date ;;
  }

  measure: count {
    type: count
    drill_fields: []
  }
}
