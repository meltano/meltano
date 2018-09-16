view: dim_opportunitystage {
  sql_table_name: analytics.dim_opportunitystage ;;

  dimension: id {
    primary_key: yes
    hidden: yes
    type: number
    sql: ${TABLE}.stage_id ;;
  }

  dimension: defaultprobability {
    label: "Default Probability"
    type: number
    sql: ${TABLE}.default_probability ;;
  }

  dimension: isactive {
    label: "Is Active"
    type: yesno
    sql: ${TABLE}.is_active ;;
  }

  dimension: isclosed {
    label: "Is Closed"
    type: yesno
    sql: ${TABLE}.is_closed ;;
  }

  dimension: iswon {
    label: "Is Won"
    type: yesno
    sql: ${TABLE}.is_won ;;
  }

  dimension: masterlabel {
    hidden: yes
    type: string
    sql: ${TABLE}.primary_label ;;
  }

  dimension: stage_state {
    type: string
    sql: ${TABLE}.stage_state ;;
  }

  dimension: mapped_stage {
    full_suggestions: yes
    label: "Stage Name"
    type: string
    sql: ${TABLE}.mapped_stage ;;
  }

  dimension: sfdc_id {
    hidden: yes
    type: string
    sql: ${TABLE}.sfdc_id ;;
  }
}
