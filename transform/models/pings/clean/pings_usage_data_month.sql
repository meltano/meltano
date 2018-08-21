WITH usage_data AS (
    SELECT * FROM {{ ref('pings_usage_data_unpacked') }}
    {% if adapter.already_exists(this.schema, this.table) and not flags.FULL_REFRESH %}
        WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
    {% endif %}
)

SELECT
  md5(usage_data.uuid || date_trunc('month', usage_data.created_at)::date)    AS unique_key,
  uuid                                                                        AS uuid,
  DATE_TRUNC('month', created_at)                                             AS created_at,
  max(edition)                                                                AS edition,
  max(auto_devops_disabled)                                                   AS auto_devops_disabled,
  max(auto_devops_enabled)                                                    AS auto_devops_enabled,
  max(boards)                                                                 AS boards,
  max(ci_builds)                                                              AS ci_builds,
  max(ci_external_pipelines)                                                  AS ci_external_pipelines,
  max(ci_internal_pipelines)                                                  AS ci_internal_pipelines,
  max(ci_pipeline_config_auto_devops)                                         AS ci_pipeline_config_auto_devops,
  max(ci_pipeline_config_repository)                                          AS ci_pipeline_config_repository,
  max(ci_pipeline_schedules)                                                  AS ci_pipeline_schedules,
  max(ci_runners)                                                             AS ci_runners,
  max(ci_triggers)                                                            AS ci_triggers,
  max(clusters)                                                               AS clusters,
  max(clusters_applications_helm)                                             AS clusters_applications_helm,
  max(clusters_applications_ingress)                                          AS clusters_applications_ingress,
  max(clusters_applications_prometheus)                                       AS clusters_applications_prometheus,
  max(clusters_applications_runner)                                           AS clusters_applications_runner,
  max(clusters_disabled)                                                      AS clusters_disabled,
  max(clusters_enabled)                                                       AS clusters_enabled,
  max(clusters_platforms_gke)                                                 AS clusters_platforms_gke,
  max(clusters_platforms_user)                                                AS clusters_platforms_user,
  max(deploy_keys)                                                            AS deploy_keys,
  max(deployments)                                                            AS deployments,
  max(environments)                                                           AS environments,
  max(gcp_clusters)                                                           AS gcp_clusters,
  max(groups)                                                                 AS groups,
  max(in_review_folder)                                                       AS in_review_folder,
  max(issues)                                                                 AS issues,
  max(keys)                                                                   AS keys,
  max(labels)                                                                 AS labels,
  max(lfs_objects)                                                            AS lfs_objects,
  max(merge_requests)                                                         AS merge_requests,
  max(milestones)                                                             AS milestones,
  max(notes)                                                                  AS notes,
  max(pages_domains)                                                          AS pages_domains,
  max(projects_prometheus_active)                                             AS projects_prometheus_active,
  max(projects)                                                               AS projects,
  max(projects_imported_from_github)                                          AS projects_imported_from_github,
  max(protected_branches)                                                     AS protected_branches,
  max(releases)                                                               AS releases,
  max(remote_mirrors)                                                         AS remote_mirrors,
  max(snippets)                                                               AS snippets,
  max(todos)                                                                  AS todos,
  max(uploads)                                                                AS uploads,
  max(web_hooks)                                                              AS web_hooks
FROM usage_data
GROUP BY 1, 2, 3

