WITH usage_pings AS (
    SELECT *
    FROM {{ ref('usage_data_clean') }}
),

vers_pings AS (
    SELECT *
    FROM {{ ref('version_checks_clean') }}
)

  /*
  Combine version and usage pings together. Generally prefer the data from usage
  over version pings.
  */
SELECT
  coalesce(udc.clean_url, vcc.clean_url)         AS clean_domain,
  coalesce(udc.raw_domain, vcc.clean_full_url)   AS clean_full_domain,
  max(coalesce(vcc.referer_url, udc.raw_domain)) AS raw_domain,
  max(greatest(udc.version, vcc.gitlab_version)) AS gitlab_version,
  max(greatest(udc.updated_at, vcc.updated_at))  AS ping_date,
  max(greatest(udc.host_id, vcc.host_id))        AS host_id,
  max(udc.stats :: TEXT) :: JSON                 AS ping_usage_data,
  max(vcc.request_data :: TEXT) :: JSON          AS ping_version_data,
  max(udc.active_user_count)                     AS active_user_count,
  max(udc.edition)                               AS gitlab_edition,
  string_agg(DISTINCT udc.installation_type :: TEXT, ', ')       AS installation_type,
  string_agg(DISTINCT udc.license_id :: TEXT, ', ')       AS license_id,
  max(udc.mattermost_enabled :: TEXT) :: BOOLEAN AS mattermost_enabled


FROM usage_pings AS udc

  FULL OUTER JOIN vers_pings AS vcc
    ON udc.clean_url = vcc.clean_url
       AND udc.raw_domain = vcc.clean_full_url
GROUP BY
  clean_domain,
  clean_full_domain

