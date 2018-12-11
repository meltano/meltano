view: region {
  sql_table_name:
    gitlab.region
    ;;

  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: name {
    description: "Carbon region long name"
    type: string
    sql: ${TABLE}.dnoregion;;
  }

  dimension: short_name {
    description: "Carbon region short name"
    type: string
    sql: ${TABLE}.shortname;;
  }

  measure: count {
    description: "Runner Count"
    type: count
    sql: ${TABLE}.id;;
  }
}
