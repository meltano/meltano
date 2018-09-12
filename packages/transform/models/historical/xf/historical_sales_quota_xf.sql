with agent_mapping as (

	SELECT *
	FROM {{ref('historical_sfdc_agent_mapping')}}

), base as ( 

	SELECT *
	FROM {{ref('historical_sales_quota')}}

), jan_17 as (

	SELECT '2017-01-01'::date as quota_month,
			account_owner, 
			january_2017
	FROM base

), feb_17 as (

	SELECT '2017-02-01'::date as quota_month,
			account_owner, 
			february_2017
	FROM base

), mar_17 as (

	SELECT '2017-03-01'::date as quota_month,
			account_owner, 
			march_2017
	FROM base

), apr_17 as (

	SELECT '2017-04-01'::date as quota_month,
			account_owner, 
			april_2017
	FROM base

), may_17 as (

	SELECT '2017-05-01'::date as quota_month,
			account_owner, 
			may_2017
	FROM base

), jun_17 as (

	SELECT '2017-06-01'::date as quota_month,
			account_owner, 
			june_2017
	FROM base

), jul_17 as (

	SELECT '2017-07-01'::date as quota_month,
			account_owner, 
			july_2017
	FROM base

), aug_17 as (

	SELECT '2017-08-01'::date as quota_month,
			account_owner, 
			august_2017
	FROM base

), sep_17 as (

	SELECT '2017-09-01'::date as quota_month,
			account_owner, 
			september_2017
	FROM base

), oct_17 as (

	SELECT '2017-10-01'::date as quota_month,
			account_owner, 
			october_2017
	FROM base

), nov_17 as (

	SELECT '2017-11-01'::date as quota_month,
			account_owner, 
			november_2017
	FROM base

), dec_17 as (

	SELECT '2017-12-01'::date as quota_month,
			account_owner, 
			december
	FROM base

), jan_18 as (

	SELECT '2018-01-01'::date as quota_month,
			account_owner, 
			january_2018
	FROM base

), feb_18 as (

	SELECT '2018-02-01'::date as quota_month,
			account_owner, 
			february_2018
	FROM base

), mar_18 as (

	SELECT '2018-03-01'::date as quota_month,
			account_owner, 
			march_2018
	FROM base

), apr_18 as (

	SELECT '2018-04-01'::date as quota_month,
			account_owner, 
			april_2018
	FROM base

), may_18 as (

	SELECT '2018-05-01'::date as quota_month,
			account_owner, 
			may_2018
	FROM base

), jun_18 as (

	SELECT '2018-06-01'::date as quota_month,
			account_owner, 
			june_2018
	FROM base

), jul_18 as (

	SELECT '2018-07-01'::date as quota_month,
			account_owner, 
			july_2018
	FROM base

), aug_18 as (

	SELECT '2018-08-01'::date as quota_month,
			account_owner, 
			august_2018
	FROM base

), sep_18 as (

	SELECT '2018-09-01'::date as quota_month,
			account_owner, 
			september_2018
	FROM base

), oct_18 as (

	SELECT '2018-10-01'::date as quota_month,
			account_owner, 
			october_2018
	FROM base

), nov_18 as (

	SELECT '2018-11-01'::date as quota_month,
			account_owner, 
			november_2018
	FROM base

), dec_18 as (

	SELECT '2018-12-01'::date as quota_month,
			account_owner, 
			december_2018
	FROM base
), unioned as (

	SELECT * FROM jan_17
	UNION ALL
	SELECT * FROM feb_17
	UNION ALL
	SELECT * FROM mar_17
	UNION ALL
	SELECT * FROM apr_17
	UNION ALL
	SELECT * FROM may_17
	UNION ALL
	SELECT * FROM jun_17
	UNION ALL
	SELECT * FROM jul_17
	UNION ALL
	SELECT * FROM aug_17
	UNION ALL
	SELECT * FROM sep_17
	UNION ALL
	SELECT * FROM oct_17
	UNION ALL
	SELECT * FROM nov_17
	UNION ALL
	SELECT * FROM dec_17
	UNION ALL
	SELECT * FROM jan_18
	UNION ALL
	SELECT * FROM feb_18
	UNION ALL
	SELECT * FROM mar_18
	UNION ALL
	SELECT * FROM apr_18
	UNION ALL
	SELECT * FROM may_18
	UNION ALL
	SELECT * FROM jun_18
	UNION ALL
	SELECT * FROM jul_18
	UNION ALL
	SELECT * FROM aug_18
	UNION ALL
	SELECT * FROM sep_18
	UNION ALL
	SELECT * FROM oct_18
	UNION ALL
	SELECT * FROM nov_18
	UNION ALL
	SELECT * FROM dec_18

), final as (

SELECT quota_month,
		account_owner,
		"january_2017" as quota
FROM unioned

)

SELECT *
FROM final
LEFT JOIN agent_mapping
ON UPPER(final.account_owner) = UPPER(agent_mapping.account_owner_name)
