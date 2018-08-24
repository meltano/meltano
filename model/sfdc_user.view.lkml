view: sfdc_user {
  sql_table_name: analytics.users ;;
  label: "SFDC User"

  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.id ;;
  }

  dimension: department {
    type: string
    sql: ${TABLE}.department ;;
  }

  dimension: manager_name {
    type: string
    sql: ${TABLE}.manager_name ;;
  }

  dimension: name {
    type: string
    sql: ${TABLE}.name ;;
  }

  dimension: email {
    type: string
    sql: ${TABLE}.email ;;
  }

  dimension: team {
    type: string
    sql: ${TABLE}.team ;;
  }

  dimension: title {
    type: string
    sql: ${TABLE}.title ;;
  }

  dimension: role_name {
    type: string
    sql:  ${TABLE}.role_name ;;
  }

  dimension: manager_id {
    hidden: yes
    type:  string
    sql: ${TABLE}.manager_id ;;
  }

  dimension: employee_tags {
    type: string
    sql: ${TABLE}.employee_tags ;;
  }

  dimension: is_active {
    type: yesno
    sql: ${TABLE}.is_active ;;
  }
}
