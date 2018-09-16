view: bookings_goal {
  sql_table_name: historical.iacv_monthly_goals ;;

  dimension: goal_month  {
    datatype: date
    primary_key: yes
    type: date
    sql: ${TABLE}.date ;;
  }

  dimension: iacv {
    hidden: yes
    label: "IACV Goal"
    sql: ${TABLE}.iacv_goal ;;
  }

  measure: total_iacv {
    label: "Total IACV"
    type: sum
    sql: ${iacv} ;;
  }
}
