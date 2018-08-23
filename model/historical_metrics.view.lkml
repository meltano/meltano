view: historical_metrics {
  # # You can specify the table name if it's different from the view name:
  sql_table_name: analytics.historical_metrics ;;
  #
  # Define your dimensions and measures here, like this:
  dimension: id {
    type: number
    hidden: yes
    primary_key: yes
    sql: ${TABLE}.primary_key ;;
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

  measure: revenue {
    description: "Total Revenue"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.total_revenue ;;
  }

  measure: users {
    description: "Total Licensed Users"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.licensed_users ;;
  }

  measure: revenue_per_user {
    description: "Total Revenue Per User (Annualized)"
    type: sum
    value_format: "$#,##0.0"
    sql: ${TABLE}.revenue_per_user ;;
  }

  measure: com_paid_users {
    description: "GitLab.com Paid Users"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.com_paid_users ;;
  }

  measure: core_self_host {
    description: "Total Self Hosted Core Instances"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.active_core_hosts ;;
  }

  measure: com_availability {
    description: "GitLab.com Availability"
    type: sum
    value_format: "0.00\%"
    sql: ${TABLE}.com_availability ;;
  }

  measure: com_response_time {
    description: "GitLab.com Response Time"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.com_response_time ;;
  }

  measure: com_active_users_thirty {
    description: "GitLab.com Active Users Over 30 Days"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.com_active_30_day_users ;;
  }

  measure: com_projects {
    description: "Total GitLab.com Projects"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.com_projects ;;
  }

  measure: ending_cash {
    description: "Total Ending Cash"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.ending_cash ;;
  }

  measure: ending_loc {
    description: "Total Line of Credit"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.ending_loc ;;
  }

  measure: cash_change {
    description: "Total Cash Change"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.cash_change ;;
  }

  measure: avg_monthly_burn {
    description: "Averaage Monthly Burn"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.avg_monthly_burn ;;
  }

  measure: days_outstanding {
    description: "A/R Days Oustanding"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.days_outstanding ;;
  }

  measure: cash_remaining_in_months {
    description: "Cash Remaining In Months"
    type: sum
    value_format: "#,##0"
    sql: ${TABLE}.cash_remaining ;;
  }

  measure: rep_prod {
    description: "Rep Productivity"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.rep_prod_annualized ;;
  }

  measure: cac {
    description: "Total Customer Acquisition Cost"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.cac ;;
  }

  measure: ltv {
    description: "Customer Life Time Value"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.ltv ;;
  }

  measure: ltv_to_cac_ratio {
    description: "LTV to CAC Ratio"
    type: sum
    value_format: "#,##0.0"
    sql: ${TABLE}.ltv_to_cac ;;
  }

  measure: cac_ratio {
    description: "CAC Ratio"
    type: sum
    value_format: "#,##0.0"
    sql: ${TABLE}.cac_ratio ;;
  }

  measure: magic_number {
    description: "Magic Number"
    type: sum
    value_format: "#,##0.0"
    sql: ${TABLE}.magic_number ;;
  }

  measure: sales_efficiency {
    description: "Sales Efficiency"
    type: sum
    value_format: "#,##0.0"
    sql: ${TABLE}.sales_efficiency ;;
  }

  measure: gross_burn_rate {
    description: "Gross Burn Rate"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.gross_burn_rate ;;
  }

  measure: capital_consumption {
    description: "Capital Consumption"
    type: sum
    value_format: "$#,##0"
    sql: ${TABLE}.capital_consumption ;;
  }

}
