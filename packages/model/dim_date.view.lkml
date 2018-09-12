view: dim_date {
  label: "Date Expansion"
  sql_table_name: analytics.dim_date ;;

  dimension_group: date_actual {
    label: "Actual"
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
    sql: ${TABLE}.date_actual ;;
  }

  dimension: date_dim_id {
    hidden: yes
    type: number
    sql: ${TABLE}.date_dim_id ;;
  }

#   dimension: day_name {
#     type: string
#     sql: ${TABLE}.day_name ;;
#   }
#
#   dimension: day_of_month {
#     type: number
#     sql: ${TABLE}.day_of_month ;;
#   }
#
  dimension: day_of_quarter {
    type: number
    sql: ${TABLE}.day_of_quarter ;;
  }
#
#   dimension: day_of_week {
#     type: number
#     sql: ${TABLE}.day_of_week ;;
#   }
#
#   dimension: day_of_year {
#     type: number
#     sql: ${TABLE}.day_of_year ;;
#   }
#
#   dimension: day_suffix {
#     type: string
#     sql: ${TABLE}.day_suffix ;;
#   }
#
#   dimension: epoch {
#     type: number
#     sql: ${TABLE}.epoch ;;
#   }
#
#   dimension_group: first_day_of_month {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.first_day_of_month ;;
#   }
#
#   dimension_group: first_day_of_quarter {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.first_day_of_quarter ;;
#   }
#
#   dimension_group: first_day_of_week {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.first_day_of_week ;;
#   }
#
#   dimension_group: first_day_of_year {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.first_day_of_year ;;
#   }
#
#   dimension_group: last_day_of_month {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.last_day_of_month ;;
#   }
#
#   dimension_group: last_day_of_quarter {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.last_day_of_quarter ;;
#   }
#
#   dimension_group: last_day_of_week {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.last_day_of_week ;;
#   }
#
#   dimension_group: last_day_of_year {
#     type: time
#     timeframes: [
#       raw,
#       date,
#       week,
#       month,
#       quarter,
#       year
#     ]
#     convert_tz: no
#     datatype: date
#     sql: ${TABLE}.last_day_of_year ;;
#   }
#
#   dimension: mmddyyyy {
#     type: string
#     sql: ${TABLE}.mmddyyyy ;;
#   }
#
#   dimension: mmyyyy {
#     type: string
#     sql: ${TABLE}.mmyyyy ;;
#   }
#
#   dimension: month_actual {
#     type: number
#     sql: ${TABLE}.month_actual ;;
#   }
#
#   dimension: month_name {
#     type: string
#     sql: ${TABLE}.month_name ;;
#   }
#
#   dimension: month_name_abbreviated {
#     type: string
#     sql: ${TABLE}.month_name_abbreviated ;;
#   }
#
#   dimension: quarter_actual {
#     type: number
#     sql: ${TABLE}.quarter_actual ;;
#   }
#
#   dimension: quarter_name {
#     type: string
#     sql: ${TABLE}.quarter_name ;;
#   }
#
#   dimension: week_of_month {
#     type: number
#     sql: ${TABLE}.week_of_month ;;
#   }
#
#   dimension: week_of_year {
#     type: number
#     sql: ${TABLE}.week_of_year ;;
#   }
#
#   dimension: week_of_year_iso {
#     type: string
#     sql: ${TABLE}.week_of_year_iso ;;
#   }
#
#   dimension: weekend_indr {
#     type: yesno
#     sql: ${TABLE}.weekend_indr ;;
#   }
#
#   dimension: year_actual {
#     type: number
#     sql: ${TABLE}.year_actual ;;
#   }
#
#   dimension: yyyymm {
#     type: string
#     sql: ${TABLE}.yyyymm ;;
#   }
#
#   dimension: yyyyqq {
#     type: string
#     sql: ${TABLE}.yyyyqq ;;
#   }
#
#   measure: count {
#     type: count
#     drill_fields: [day_name, month_name, quarter_name]
#   }
}
