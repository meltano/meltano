view: sfdc_closed_deals_acv {
  sql_table_name: analytics.sfdc_closed_deals_acv ;;
  label: "Salesforce Closed Deals ACV"
  #
  dimension: sales_type {
    description: "Sales Type"
    type: string
    sql: ${TABLE}.sales_type ;;
  }
  #
  dimension: sales_path {
    description: "Sales Path"
    type: string
    sql: ${TABLE}.sales_path ;;
  }
  #
  dimension: owner {
    description: "Opportunity Owner"
    type: string
    drill_fields: [sales_type,sales_path,segment,closedate_month]
    sql: ${TABLE}.owner ;;
  }
  #
  dimension: segment {
    description: "Segment"
    type: string
    sql: ${TABLE}.account_segment ;;
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
  measure: acv {
    description: "Closed Deal ACV"
    type: sum
    value_format: "$#,##0"
    drill_fields: [sales_type,sales_path,segment,owner,closedate_month]
    sql: ${TABLE}.acv ;;
  }
  #
  measure: closed_deals {
    description: "Closed Deals"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.closed_deals ;;
  }

}
