with base as (

SELECT max(updated_at)::date FROM {{ref('historical_headcount')}}

),  maxdate as (

    select  CURRENT_DATE - max(max)::date as last_update_diff
    from base

)

select *
from maxdate 
WHERE last_update_diff >= '30'
