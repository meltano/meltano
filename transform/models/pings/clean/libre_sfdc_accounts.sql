with libre_agg as (
  SELECT * FROM {{ ref('libre_agg_hosts') }}
),

libre AS (
  SELECT *
  FROM {{ ref('libre_hosts') }}
),

host_data AS (
    SELECT *
    FROM libre
    JOIN libre_agg ON libre.clean_domain = libre_agg.the_clean_url
  )

  -- This generates the host records to be uploaded to SFDC
SELECT
  sf.id                                                         AS Account__c,
  host.clean_full_domain                                        AS Name,
  host.raw_domain                                               AS Original_Hostname__c,
  host.active_user_count                                        AS Host_Users__c,
  host.installation_type                                        AS Installation_Type__c,
  host.ping_date                                                AS Last_Ping__c,
  host.ping_usage_data :: TEXT                                  AS Raw_Usage_Stats__c,
  host.ping_version_data :: TEXT                                AS Raw_Version_Stats__c,
  'https://version.gitlab.com/servers/' || host.host_id :: TEXT AS Version_Link__c,
  host.gitlab_version                                           AS GitLab_Version__c,
  host.gitlab_edition                                           AS GitLab_edition__c,
  host.license_id                                               AS License_Ids__c,
  host.mattermost_enabled                                       AS Mattermost_Enabled__c,
  host.source                                                   AS Host_Data_Source__c
FROM sfdc.account sf
  INNER JOIN host_data AS host
    ON host.company_name = sf.name
WHERE sf.isdeleted = FALSE
      AND sf.type != 'Customer'
      AND (host.active_user_count != sf.active_ce_users__c OR sf.active_ce_users__c IS NULL)
      AND sf.name NOT IN ('Microsoft', 'Amazon.com')

UNION

SELECT
  sf.id                                                         AS Account__c,
  host.clean_full_domain                                        AS Name,
  host.raw_domain                                               AS Original_Hostname__c,
  host.active_user_count                                        AS Host_Users__c,
  host.installation_type                                        AS Installation_Type__c,
  host.ping_date                                                AS Last_Ping__c,
  host.ping_usage_data :: TEXT                                  AS Raw_Usage_Stats__c,
  host.ping_version_data :: TEXT                                AS Raw_Version_Stats__c,
  'https://version.gitlab.com/servers/' || host.host_id :: TEXT AS Version_Link__c,
  host.gitlab_version                                           AS GitLab_Version__c,
  host.gitlab_edition                                           AS GitLab_edition__c,
  host.license_id                                               AS License_Ids__c,
  host.mattermost_enabled                                       AS Mattermost_Enabled__c,
  host.source                                                   AS Host_Data_Source__c
FROM sfdc.account sf
  INNER JOIN host_data AS host
    ON host.clean_domain = regexp_replace(sf.website, '^(http(s)?\://)?www\.', '')
WHERE sf.isdeleted = FALSE
      AND sf.type != 'Customer'
      AND (host.active_user_count != sf.active_ce_users__c OR sf.active_ce_users__c IS NULL)
      AND sf.name NOT IN ('Microsoft', 'Amazon.com')

