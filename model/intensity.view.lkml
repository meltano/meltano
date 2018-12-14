view: intensity {
  sql_table_name:
    gitlab.intensity
    ;;

  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: entry_id {
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: forecast {
    description: "Selected forecast in carbon data"
    type: number
    sql: ${TABLE}.forecast;;
  }

  dimension: index {
    description: "Selected index range in carbon data"
    type: string
    sql: ${TABLE}.index;;
  }
}
