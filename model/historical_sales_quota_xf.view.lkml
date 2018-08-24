view: historical_sales_quota_xf {
  sql_table_name: analytics.historical_sales_quota_xf ;;

  dimension: key {
    primary_key: yes
    type: string
    hidden: yes
    sql: md5(${account_owner_id} || ${quota_month_month}) ;;
  }

  dimension: account_owner {
    type: string
    sql: ${TABLE}.account_owner ;;
  }

  dimension: account_owner_id {
    type: string
    sql: ${TABLE}.account_owner_id ;;
  }

  dimension: account_owner_name {
    type: string
    sql: ${TABLE}.account_owner_name ;;
  }

  measure: quota {
    type: sum
    sql: CASE WHEN ${TABLE}.quota = 'N/A' THEN NULL ELSE ${TABLE}.quota::float8 END ;;
  }

  dimension_group: quota_month {
    type: time
    timeframes: [
      date,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.quota_month ;;
  }

  dimension: months_since_adjusted_start_date {
    type: number
    sql: (DATE_PART('year', date_trunc('month', ${f_opportunity.closedate_date}::date)) - DATE_PART('year', ${historical_sales_quota.adjusted_start_date_date}::date)) * 12 +
              (DATE_PART('month', date_trunc('month', ${f_opportunity.closedate_date}::date)) - DATE_PART('month', ${historical_sales_quota.adjusted_start_date_date}::date)) ;;
  }

  measure: count {
    type: count
    drill_fields: [account_owner_name]
  }
}
