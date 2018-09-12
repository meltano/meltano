
WITH zuora_subs AS (

    SELECT *
    FROM {{ ref('zuora_subscription') }}
    WHERE
        subscription_status = 'Active'
    AND (lower(exclude_from_renewal_report) != 'yes' OR exclude_from_renewal_report IS NULL)

),

    zuora_accts AS (

      SELECT *
      FROM {{ ref('zuora_account') }}

  ),

    zuora_rateplan AS (

      SELECT *
      FROM {{ ref('zuora_rate_plan') }}

  ),

    zuora_rateplancharge AS (

      SELECT *
      FROM {{ ref('zuora_rate_plan_charge') }}
      WHERE
        is_last_segment IS TRUE

  ),

     combined AS (
        SELECT
          a.*,
          s.*,
          r.*,
          rp.*,
          CASE
          WHEN s.initial_term < 12
            THEN ROW_NUMBER()
            OVER (
              PARTITION BY a.account_name
              ORDER BY s.subscription_end_date ASC )
          ELSE 1
          END     AS row_multiplier
        FROM zuora_accts a
          JOIN zuora_subs s ON s.account_id = a.account_id
          JOIN zuora_rateplan r ON r.subscription_id = s.subscription_id
          JOIN zuora_rateplancharge rp ON r.rate_plan_id = rp.rate_plan_id
    )

SELECT
  account_name,
  account_number,
  crm_id,
  subscription_name,
  subscription_end_date,
  rate_plan_name,
  mrr,
  row_multiplier * initial_term AS term
FROM combined
