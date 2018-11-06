view: runners {
  sql_table_name:
    gitlab.runners
    ;;

  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id;;
  }

  dimension: active {
    description: "GitLab Runner"
    type: yesno
    sql: ${TABLE}.active;;
  }

  dimension: description {
    description: "GitLab Runner"
    type: string
    sql: ${TABLE}.description;;
  }

  dimension: ip_address {
    description: "GitLab Runner"
    type: string
    sql: ${TABLE}.ip_address;;
  }

  dimension: is_shared {
    description: "GitLab Runner"
    type: yesno
    sql: ${TABLE}.is_shared;;
  }

  dimension: name {
    description: "GitLab Runner"
    type: string
    sql: ${TABLE}.name;;
  }

  dimension: online {
    description: "GitLab Runner"
    type: yesno
    sql: ${TABLE}.online;;
  }

  dimension: status {
    description: "GitLab Runner"
    type: string
    sql: ${TABLE}.status;;
  }

  measure: count {
    description: "Runner Count"
    type: count
    sql: ${TABLE}.id;;
  }
}
