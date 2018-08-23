view: dim_opphistory {
  sql_table_name: analytics.dim_opphistory ;;

  dimension:  opportunityid{
    # hidden: yes
    type: string
    sql: ${TABLE}.opportunityid ;;
  }

  dimension: stagename {
    label: "Stage Name"
    type: string
    sql: ${TABLE}.mapped_stage ;;
  }

  dimension: days_in_stage {
    type: number
    sql:${TABLE}.days_in_stage ;;
  }

  measure: avg_stage_days {
    label: "Average of Days in Stage"
    type: average
    sql: ${days_in_stage} ;;
    value_format: "0.#"
  }

  measure: sum_stage_days {
    label: "Total Days"
    type:  sum
    sql: ${days_in_stage} ;;
    value_format: "0.#"
  }

  measure: count_of_opps {
    type: count_distinct
    sql: ${opportunityid} ;;
  }
}
