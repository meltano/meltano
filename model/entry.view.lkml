view: entry {
  sql_table_name:
    gitlab.entry
    ;;

  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: region_id {
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: forecast {
    description: "Carbon entry intensity forecast"
    type: number
    sql: ${TABLE}.forecast;;
  }

  dimension: index {
    description: "Carbon entry intensity forecast"
    type: number
    sql: ${TABLE}.index;;
  }

  dimension_group: from {
    description: "Selected from range in carbon data"
    type: time
    timeframes: [date, week, month, year]
    convert_tz: no
    sql: ${TABLE}.from;;
  }

  dimension_group: to {
    description: "Selected to range in carbon data"
    type: time
    timeframes: [date, week, month, year]
    convert_tz: no
    sql: ${TABLE}.to;;
  }
}