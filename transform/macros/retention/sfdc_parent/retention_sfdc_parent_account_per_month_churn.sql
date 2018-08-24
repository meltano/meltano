{% macro retention_sfdc_parent_account_per_month_churn(n) %}

WITH zuora_subs AS (
    SELECT *
    FROM {{ ref('zuora_subscription') }}
    WHERE subscription_status <> ALL (ARRAY ['Draft' :: TEXT, 'Expired' :: TEXT])
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
  ),

    sfdc_acct AS (
      SELECT *
      FROM {{ ref('sfdc_account') }}
  ),

    {% for the_month in range(0, n + 1) %}

        {{ retention_sfdc_parent_account_churn_history_cte_calc(the_month) }}

        {% if  the_month != n %}

            ,

        {% else %}

        {%- endif -%}

    {% endfor %}


    {% for the_month in range(0, n + 1) %}

        {{ retention_sfdc_parent_account_churn_history_select_calc(the_month) }}

        {% if  the_month != n %}

            UNION

        {% else %}

        {%- endif -%}

    {% endfor %}


{% endmacro %}