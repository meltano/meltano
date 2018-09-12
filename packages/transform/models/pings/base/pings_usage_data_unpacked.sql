WITH usage_data AS (
    SELECT * FROM {{ ref('pings_usage_data') }}
)

SELECT
  id,
  source_ip,
  version,
  installation_type,
  active_user_count,
  created_at,
  mattermost_enabled,
  uuid,
  edition,
  CASE
    WHEN version ~ 'ee'
      THEN 'EE'
    ELSE 'CE' END                                                   AS main_edition,
  CASE
--     Comes from https://gitlab.com/gitlab-org/gitlab-ee/blob/2dae25c3b780205f072833cd290e481dae436f3b/lib/gitlab/usage_data.rb#L154
    WHEN edition ~ 'CE'
      THEN 'Core'
    WHEN edition ~ 'EES'
      THEN 'Starter'
    WHEN edition ~ 'EEP'
      THEN 'Premium'
    WHEN edition ~ 'EEU'
      THEN 'Ultimate'
    WHEN edition ~ 'EE Free'
      THEN 'Core'
    WHEN edition ~ 'EE'
      THEN 'Starter'
    ELSE null END                                                  AS edition_type,
  trim(TRAILING '.' FROM (regexp_matches(version, '(\d{1,2}\.\d{1,2}\.)')) [1])
                                                                   AS major_version,
  hostname,
  host_id,
  (stats -> 'auto_devops_disabled') :: TEXT :: NUMERIC             AS auto_devops_disabled,
  (stats -> 'auto_devops_enabled') :: TEXT :: NUMERIC              AS auto_devops_enabled,
  (stats -> 'boards') :: TEXT :: NUMERIC                           AS boards,
  (stats -> 'ci_builds') :: TEXT :: NUMERIC                        AS ci_builds,
  (stats -> 'ci_external_pipelines') :: TEXT :: NUMERIC            AS ci_external_pipelines,
  (stats -> 'ci_internal_pipelines') :: TEXT :: NUMERIC            AS ci_internal_pipelines,
  (stats -> 'ci_pipeline_config_auto_devops') :: TEXT :: NUMERIC   AS ci_pipeline_config_auto_devops,
  (stats -> 'ci_pipeline_config_repository') :: TEXT :: NUMERIC    AS ci_pipeline_config_repository,
  (stats -> 'ci_pipeline_schedules') :: TEXT :: NUMERIC            AS ci_pipeline_schedules,
  (stats -> 'ci_runners') :: TEXT :: NUMERIC                       AS ci_runners,
  (stats -> 'ci_triggers') :: TEXT :: NUMERIC                      AS ci_triggers,
  (stats -> 'clusters') :: TEXT :: NUMERIC                         AS clusters,
  (stats -> 'clusters_applications_helm') :: TEXT :: NUMERIC       AS clusters_applications_helm,
  (stats -> 'clusters_applications_ingress') :: TEXT :: NUMERIC    AS clusters_applications_ingress,
  (stats -> 'clusters_applications_prometheus') :: TEXT :: NUMERIC AS clusters_applications_prometheus,
  (stats -> 'clusters_applications_runner') :: TEXT :: NUMERIC     AS clusters_applications_runner,
  (stats -> 'clusters_disabled') :: TEXT :: NUMERIC                AS clusters_disabled,
  (stats -> 'clusters_enabled') :: TEXT :: NUMERIC                 AS clusters_enabled,
  (stats -> 'clusters_platforms_gke') :: TEXT :: NUMERIC           AS clusters_platforms_gke,
  (stats -> 'clusters_platforms_user') :: TEXT :: NUMERIC          AS clusters_platforms_user,
  (stats -> 'deploy_keys') :: TEXT :: NUMERIC                      AS deploy_keys,
  (stats -> 'deployments') :: TEXT :: NUMERIC                      AS deployments,
  (stats -> 'environments') :: TEXT :: NUMERIC                     AS environments,
  (stats -> 'gcp_clusters')::text::NUMERIC                         AS gcp_clusters,
  (stats -> 'groups') :: TEXT :: NUMERIC                           AS groups,
  (stats -> 'in_review_folder') :: TEXT :: NUMERIC                 AS in_review_folder,
  (stats -> 'issues') :: TEXT :: NUMERIC                           AS issues,
  (stats -> 'keys') :: TEXT :: NUMERIC                             AS keys,
  (stats -> 'labels') :: TEXT :: NUMERIC                           AS labels,
  (stats -> 'lfs_objects') :: TEXT :: NUMERIC                      AS lfs_objects,
  (stats -> 'merge_requests') :: TEXT :: NUMERIC                   AS merge_requests,
  (stats -> 'milestones') :: TEXT :: NUMERIC                       AS milestones,
  (stats -> 'notes') :: TEXT :: NUMERIC                            AS notes,
  (stats -> 'pages_domains') :: TEXT :: NUMERIC                    AS pages_domains,
  (stats -> 'projects_prometheus_active')::text::numeric           AS projects_prometheus_active,
  (stats -> 'projects') :: TEXT :: NUMERIC                         AS projects,
  (stats -> 'projects_imported_from_github') :: TEXT :: NUMERIC    AS projects_imported_from_github,
  (stats -> 'protected_branches') :: TEXT :: NUMERIC               AS protected_branches,
  (stats -> 'releases') :: TEXT :: NUMERIC                         AS releases,
  (stats -> 'remote_mirrors') :: TEXT :: NUMERIC                   AS remote_mirrors,
  (stats -> 'snippets') :: TEXT :: NUMERIC                         AS snippets,
  (stats -> 'todos') :: TEXT :: NUMERIC                            AS todos,
  (stats -> 'uploads') :: TEXT :: NUMERIC                          AS uploads,
  (stats -> 'web_hooks') :: TEXT :: NUMERIC                        AS web_hooks
FROM usage_data
{% if adapter.already_exists(this.schema, this.table) and not flags.FULL_REFRESH %}
    WHERE created_at > (SELECT max(created_at) FROM {{ this }})
{% endif %}
