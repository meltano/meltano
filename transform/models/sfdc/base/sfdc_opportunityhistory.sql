WITH base AS (
    SELECT
      *,
      lead(createddate)
      OVER (
        PARTITION BY opportunityid
        ORDER BY createddate ) - opportunityhistory.createddate AS time_in_stage
    FROM sfdc.opportunityhistory
)

SELECT
  *,
  CASE
    WHEN time_in_stage IS NULL OR extract(EPOCH FROM time_in_stage) / (3600 * 24) = 0
        THEN 0.0001
    ELSE
        coalesce(extract(EPOCH FROM time_in_stage) / (3600 * 24), 0.0001) END AS days_in_stage
FROM base