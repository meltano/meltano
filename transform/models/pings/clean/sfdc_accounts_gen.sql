-- This generates the records that need to be uploaded to SFDC as new accounts

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
),

name_match AS (
/*
This takes host files (non IP), matches to SFDC on name, and gets those
host files (uniquely identified by the clean_domain) where there is no name match in salesforce.
 */
  SELECT
    max(company_name)            AS name,
    clean_domain                 AS website
  FROM host_data AS lah
    LEFT OUTER JOIN
    (
      SELECT
        id,
        name,
        type
      FROM sfdc.account) AS sf
      ON lah.company_name = sf.name
      AND sf.type != 'Customer'
  WHERE sf.name IS NULL
        AND clean_domain !~ '\d+\.\d+.\d+\.\d+'
        AND lah.company_name NOT IN ('Microsoft', 'Amazon.com')
  GROUP BY clean_domain
)

/*
Takes the remaining host records, attempts to match with SFDC based on website,
and returns those where there is no match.
 */
SELECT
  max(name)                    AS name,
  website                      AS website,
  'Prospect - CE User' :: TEXT AS type,
  '00561000000mpHTAAY' :: TEXT AS ownerid,
  'True' :: BOOLEAN            AS using_ce__c,
  'CE Download' :: TEXT        AS accountsource
FROM name_match AS lah
LEFT OUTER JOIN
  (
    SELECT
      sfdc.id,
      sfdc.type,
      sfdc.website                                              AS original,
      regexp_replace(sfdc.website, '^(http(s)?\://)?www\.', '') AS fixed
    FROM sfdc.account AS sfdc
    WHERE website IS NOT NULL
  ) AS sf
    ON lah.website = sf.fixed
    AND sf.type != 'Customer'
WHERE sf.fixed IS NULL
      AND website !~ '\d+\.\d+.\d+\.\d+'
      AND lah.name NOT IN ('Microsoft', 'Amazon.com')
GROUP BY website

ORDER BY name

