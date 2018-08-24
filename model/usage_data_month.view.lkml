view: usage_data_month {
  sql_table_name: analytics.pings_usage_data_boolean ;;

  dimension: created_at_month {
    type: date_month
    sql: ${TABLE}.created_at ;;
  }

  dimension: edition {
    type: string
    sql: ${TABLE}.edition ;;
  }

  # UUID

  dimension: uuid {
    type: string
    sql: ${TABLE}.uuid ;;
  }

  measure: distinct_uuid_count {
    type: count_distinct
    sql: ${uuid} ;;
  }

  # Usage metrics

  dimension: auto_devops_count {
    type: number
    sql: ${TABLE}.auto_devops_enabled ;;
  }

  measure: auto_devops_instance_count {
    type: sum
    sql: ${TABLE}.auto_devops_enabled_active ;;
  }

  dimension: boards_count {
    type: number
    sql: ${TABLE}.boards ;;
  }

  measure: boards_instance_count {
    type: sum
    sql: ${TABLE}.boards_active ;;
  }

  dimension: ci_builds_count {
    type: number
    sql: ${TABLE}.ci_builds ;;
  }

  measure: ci_builds_instance_count {
    type: sum
    sql: ${TABLE}.ci_builds_active ;;
  }

  dimension: deployments_count {
    type: number
    sql: ${TABLE}.deployments ;;
  }

  measure: deployments_instance_count {
    type: sum
    sql: ${TABLE}.deployments_active ;;
  }

  dimension: environments_count {
    type: number
    sql: ${TABLE}.environments ;;
  }

  measure: environments_instance_count {
    type: sum
    sql: ${TABLE}.environments_active ;;
  }

  dimension: gcp_clusters_count {
    type: number
    sql: ${TABLE}.gcp_clusters ;;
  }

  measure: gcp_clusters_instance_count {
    type: sum
    sql: ${TABLE}.gcp_clusters_active ;;
  }

  dimension: groups_count {
    type: number
    sql: ${TABLE}.groups ;;
  }

  measure: groups_instance_count {
    type: sum
    sql: ${TABLE}.groups_active ;;
  }

  dimension: issues_count {
    type: number
    sql: ${TABLE}.issues ;;
  }

  measure: issues_instance_count {
    type: sum
    sql: ${TABLE}.issues_active ;;
  }

  dimension: lfs_objects_count {
    type: number
    sql: ${TABLE}.lfs_objects ;;
  }

  measure: lfs_objects_instance_count {
    type: sum
    sql: ${TABLE}.lfs_objects_active ;;
  }

  dimension: merge_requests_count {
    type: number
    sql: ${TABLE}.merge_requests ;;
  }

  measure: merge_requests_instance_count {
    type: sum
    sql: ${TABLE}.merge_requests_active ;;
  }

  dimension: milestones_count {
    type: number
    sql: ${TABLE}.milestones ;;
  }

  measure: milestones_instance_count {
    type: sum
    sql: ${TABLE}.milestones_active ;;
  }

  dimension: projects_count {
    type: number
    sql: ${TABLE}.projects ;;
  }

  measure: projects_instance_count {
    type: sum
    sql: ${TABLE}.projects_active ;;
  }

  dimension: projects_prometheus_active_count {
    type: number
    sql: ${TABLE}.projects_prometheus_active ;;
  }

  measure: projects_prometheus_active_instance_count {
    type: sum
    sql: ${TABLE}.projects_prometheus_active_active ;;
  }

}
