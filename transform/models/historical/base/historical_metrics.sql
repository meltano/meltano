WITH source AS (

	SELECT *
	FROM historical.metrics

), renamed AS (


	SELECT uniquekey as primary_key,
			month::date as month_of,
			total_revenue::decimal as total_revenue,
			licensed_users::decimal as licensed_users,
			rev_per_user::decimal  as revenue_per_user,
			com_paid_users::decimal as com_paid_users,
			active_core_hosts::decimal as active_core_hosts,
			com_availability::decimal as com_availability,
			com_response_time::decimal as com_response_time,
			com_active_30_day_users::decimal as com_active_30_day_users,
			com_projects::decimal as com_projects,
			ending_cash::decimal as ending_cash,
			ending_loc::decimal as ending_loc,
			cash_change::decimal as cash_change,
			avg_monthly_burn::decimal as avg_monthly_burn,
			days_outstanding::decimal,
			cash_remaining::decimal,
			rep_prod_annualized::decimal as rep_prod_annualized,
			cac::decimal as cac, 
			ltv::decimal as ltv, 
			ltv_to_cac::decimal,
			cac_ratio::decimal,
			magic_number::decimal, 
			sales_efficiency::decimal, 
			gross_burn_rate::decimal as gross_burn_rate,
			cap_consumption::decimal as capital_consumption,
			
			--metadata
			TIMESTAMP 'epoch' + updated_at * INTERVAL '1 second' as updated_at
			
	FROM source

)

SELECT *
FROM renamed