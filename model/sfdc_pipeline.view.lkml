view: sfdc_pipeline {
  sql_table_name: analytics.sfdc_pipeline ;;
  #
  dimension: type {
    description: "Opportunity Type"
    type: string
    sql: ${TABLE}.sales_type ;;
  }
  #
  dimension: stagename {
    description: "Opportunity Stage"
    type: string
    sql: ${TABLE}.stage_name ;;
  }
  #
  dimension: owner {
    description: "Opportunity Owner"
    type: string
    drill_fields: [type,stagename,name,closedate_month]
    sql: ${TABLE}.owner ;;
  }
  #
  dimension: name {
    description: "Opportunity Name"
    type: string
    sql: ${TABLE}.opportunity_name ;;
  }
  dimension_group: closedate {
    description: "The date when an opportunity was closed"
    label: "Opportunity Close Date"
    type: time
    convert_tz: no
    timeframes: [date, week, month, year]
    sql: ${TABLE}.close_date ;;
  }
  #
  measure: forecasted_iacv {
    description: "Opportunity IACV"
    type: sum
    value_format: "$#,##0"
    drill_fields: [type,stagename,owner,name,closedate_month]
    sql: ${TABLE}.forecasted_iacv ;;
  }
  #
  measure: opps {
    description: "Opportunities"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.opps ;;
  }

}
