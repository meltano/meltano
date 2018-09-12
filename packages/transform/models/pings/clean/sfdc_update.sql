WITH external_combined AS (
    SELECT
      coalesce(dorg.domain, cbit.domain)                     AS domain,
      coalesce(dorg.company_name, cbit.company_name)         AS name,
      coalesce(dorg.company_industry, cbit.company_industry) AS industry,
      coalesce(dorg.company_desc, cbit.company_desc)         AS description,
      coalesce(dorg.company_emp, cbit.company_emp)           AS numberofemployees,
      coalesce(dorg.company_phone, cbit.company_phone)       AS phone
    FROM
      public.discoverorg_cache AS dorg
      FULL OUTER JOIN public.clearbit_cache AS cbit
        ON dorg.domain = cbit.domain
    WHERE
      dorg.company_name IS NOT NULL AND cbit.company_name IS NOT NULL
)

SELECT
  sf.id,
  sf.name,
  coalesce(sf.website, external_combined.domain)                                      AS website,
  coalesce(sf.industry, external_combined.industry)                                   AS industry,
  coalesce(sf.description, external_combined.description)                             AS description,
  coalesce(sf.numberofemployees :: TEXT, external_combined.numberofemployees :: TEXT) AS numberofemployees
FROM sfdc.account AS sf
  INNER JOIN external_combined ON
                                sf.name = external_combined.name
                                OR regexp_replace(sf.website, '^(http(s)?\://)?www\.', '') = external_combined.domain

