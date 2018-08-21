WITH opphistory AS (
		SELECT * FROM {{ ref('sfdc_opportunityhistory') }}
),

stages AS (
        SELECT * FROM {{ ref('sfdc_opportunitystage') }}
),

all_stages AS (
-- Gets a mapping of opp id to all mapped stages
        SELECT
          o.opportunityid,
          s.mapped_stage
        FROM opphistory o
        CROSS JOIN stages s
),

agg_days AS (
-- Gets each mapped stage in opp historr and the days in that stage
       SELECT
        s.mapped_stage,
        oh.opportunityid,
        sum(days_in_stage) AS days_in_stage
       FROM opphistory oh
       JOIN stages s
       ON oh.stagename = s.primary_label
       GROUP BY 1, 2
)

-- Gets ALL mapped stages and the appropriate value from the calculation
SELECT
    a.opportunityid,
    a.mapped_stage,
--    Each opp has a row for each stage, but gets no credit if it was never in the stage.
    CASE
        WHEN o.days_in_stage=0 THEN 0.0001
       ELSE coalesce(o.days_in_stage, 0.0001) END AS days_in_stage
FROM all_stages a
FULL OUTER JOIN agg_days o
  ON a.opportunityid=o.opportunityid
     AND a.mapped_stage=o.mapped_stage
GROUP BY 1, 2, 3