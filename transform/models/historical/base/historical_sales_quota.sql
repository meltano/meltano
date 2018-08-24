WITH source AS (

	SELECT *
	FROM historical.sales_quota

), renamed AS (


	SELECT account_owner,
			segment,
			role,
			start_date,
			adjusted_start_date,
			fte_date_ramp,
			fte_rep_productivity,
			termination_date,
			inactive,
			is_active,
			is_fte_today_ramp,
			is_fte_today_productivity,
			fte_annual_quota,
			"2017_quota_plan" as quota_plan_2017,
			"2017-01-01" as january_2017,
			"2017-02-01" as february_2017,
			"2017-03-01" as march_2017,    
			"2017-04-01" as april_2017,    
			"2017-05-01" as may_2017,    
			"2017-06-01" as june_2017,    
			"2017-07-01" as july_2017,    
			"2017-08-01" as august_2017,    
			"2017-09-01" as september_2017,    
			"2017-10-01" as october_2017,    
			"2017-11-01" as november_2017,    
			"2017-12-01" as december,    
			"2017_ytd" as ytd_2017,
			"2017_actual_quotas" as actual_quotas_2017,
			"2018_fte_quota" as fte_quota_2018,    
			"2018-01-01" as january_2018,
			"2018-02-01" as february_2018,
			"2018-03-01" as march_2018,    
			"2018-04-01" as april_2018,    
			"2018-05-01" as may_2018,    
			"2018-06-01" as june_2018,    
			"2018-07-01" as july_2018,    
			"2018-08-01" as august_2018,    
			"2018-09-01" as september_2018,    
			"2018-10-01" as october_2018,    
			"2018-11-01" as november_2018,    
			"2018-12-01" as december_2018,    
			"2018_quota_ytd" as quota_ytd_2018,
			"2018_actual_quota" as actual_quota_2018		
	FROM source

)

SELECT *
FROM renamed