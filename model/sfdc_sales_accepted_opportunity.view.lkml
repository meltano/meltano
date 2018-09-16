view: sfdc_sales_accepted_opportunity {
  sql_table_name: analytics.sfdc_sales_accepted_opportunity ;;
  label: "Salesforce Sales Accepted Opportunity"
  #
  dimension: opp_segment {
    description: "Opportunity Segment"
    type: string
    sql: ${TABLE}.opportunity_segment ;;
  }
  dimension: customer {
    description: "Customer"
    type: string
    sql: ${TABLE}.account_name ;;
  }
  #
  dimension: opportunity {
    description: "Oppportunity Name"
    type: string
    sql: ${TABLE}.opportunity_name ;;
  }
  #
  dimension: acct_num {
    description: "Acct # of Customer"
    type: string
    sql: ${TABLE}.accountnumber ;;
  }
  #
  dimension: lead_type {
    description: "Lead Type"
    type: string
    sql: ${TABLE}.generated_source ;;
  }
  #
  dimension: sales_segment {
    description: "Sales Segment"
    type: string
    sql: ${TABLE}.sales_segment ;;
  }
  #
  dimension: parent_segment {
    description: "Parent Segment"
    type: string
    sql: ${TABLE}.parent_segment ;;
  }
  #
  dimension: stagename {
    description: "Stage Opp Is In"
    type: string
    sql: ${TABLE}.stagename ;;
  }
  #
  dimension: leadsource {
    description: "Source of Lead"
    type: string
    sql: ${TABLE}.lead_source ;;
  }
  #
  dimension: type {
    description: "Deal Type"
    type: string
    sql: ${TABLE}.sales_type ;;
  }
  #
  dimension_group: sales_accepted_date {
    type: time
    timeframes: [
      raw,
      date,
      week,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.sales_accepted_date ;;
  }

  #
  measure: tcv {
    description: "TCV"
    type: sum
    sql: ${TABLE}.total_contract_value ;;
  }
  #
  measure: iacv {
    description: "IACV"
    type: sum
    sql: ${TABLE}.incremental_acv ;;
  }
  #
  measure: segment_cnt {
    description: "Count from Opp Segment"
    type: count_distinct
    sql: ${TABLE}.opp_name ;;
  }

}
