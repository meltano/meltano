view: f_snapshot_opportunity {
#   sql_table_name: analytics.f_snapshot_opportunity ;;

  label: "Historical Opportunity Snapshots"
  derived_table: {
    sql:
    SELECT *
    FROM analytics.f_snapshot_opportunity s
    JOIN analytics.dim_date d on s.snapshot_date = d.date_actual
    WHERE d.{% parameter.agg_span %} = 1
    ;;
  }

  dimension: account_id {
    hidden: yes
    type: number
    sql: ${TABLE}.account_id ;;
  }

  dimension: lead_source_id {
    hidden: yes
    type: number
    sql: ${TABLE}.lead_source_id ;;
  }

  dimension: ownerid {
    hidden: yes
    type: string
    sql:${TABLE}.ownerid ;;
  }

  dimension: opportunity_closedate {
    label:"Close Date"
    type: date
    sql: ${TABLE}.opportunity_closedate ;;
  }

  measure: total_acv {
    label: "Total ACV"
    type: sum
    sql: ${TABLE}.acv;;
    value_format_name: usd
  }

  measure: total_iacv {
    label: "Total IACV"
    type: sum
    sql: ${TABLE}.iacv ;;
    value_format_name: usd
  }

  measure: total_renewal_acv {
    label: "Total Renewal ACV"
    type: sum
    sql: ${TABLE}.renewal_acv ;;
    value_format_name: usd
  }

  measure: total_tcv {
    label: "Total TCV"
    type: sum
    sql: ${TABLE}.tcv ;;
    value_format_name: usd
  }

  parameter: agg_span {
    label: "Time Grouping"
    description: "Choose which snapshot range to view by"
    allowed_value: { label: "Weekly" value: "day_of_week" }
    allowed_value: { label: "Monthly" value: "day_of_month" }
    allowed_value: { label: "Quarterly" value: "day_of_quarter" }
    allowed_value: { label: "Yearly" value: "day_of_year" }
    default_value: "day_of_month"
    type: unquoted
  }

  dimension: opportunity_id {
    type: string
    sql: ${TABLE}.opportunity_id ;;
  }

  dimension: opportunity_name {
    label: "Name"
    type: string
    sql: ${TABLE}.opportunity_name ;;
  }

  dimension: opportunity_sales_segmentation {
    label: "Sales Segmentation"
    type: string
    sql: ${TABLE}.opportunity_sales_segmentation ;;
  }

  dimension: opportunity_stage_id {
    hidden: yes
    type: number
    sql: ${TABLE}.opportunity_stage_id ;;
  }

  dimension: opportunity_type {
    label: "Type"
    type: string
    sql: ${TABLE}.opportunity_type ;;
  }

  dimension: renewal_acv {
    type: number
    sql: ${TABLE}.renewal_acv ;;
  }

  dimension_group: sales_accepted {
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

  dimension_group: sales_qualified {
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
    sql: ${TABLE}.sales_qualified_date ;;
  }

  dimension: sales_qualified_source {
    type: string
    sql: ${TABLE}.sales_qualified_source ;;
  }

  dimension: snapshot {
    label: "Snapshot Date"
    type: date
    allow_fill: no
    sql: ${TABLE}.date_actual ;;
#     link: {
#       label: "Explore from here"
#       url: "https://gitlab.looker.com/explore/sales/f_snapshot_opportunity?f[f_snapshot_opportunity.agg_span]={{ f_snapshot_opportunity.agg_span }}&f[dim_opportunity.stage_name]={{ _filters['dim_opportunity.stage_name'] | url_encode }}&f[pipeline_change.date_range]={{ _filters['pipeline_change.date_range'] | url_encode }}&f[pipeline_change.metric_type]={{ _filters['pipeline_change.metric_type'] | url_encode }}&fields=pipeline_change.opportunity_name,pipeline_change.opportunity_type,dim_opportunitystage.mapped_stage,pipeline_change.iacv"
#     }
  }

  measure: count {
    type: count
    drill_fields: [opportunity_name]
  }
}
