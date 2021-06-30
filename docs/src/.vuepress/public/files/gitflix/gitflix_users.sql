with source as (

    select * from {{ env_var('MELTANO_LOAD_SCHEMA') }}.users

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer)                 as user_id,

        -- Profile Attributes
        name                                as name,

        -- Fix empty values and cast the age to integer
        CAST(nullif(age, '') as integer)    as age,

        -- Add an age_group categorical dimension
        case
            when CAST(nullif(age, '') as integer) < 18
                then '1 - Under 18'
            when CAST(nullif(age, '') as integer) >= 18
              and CAST(nullif(age, '') as integer) < 40
                then '2 - 20 to 40'
            when CAST(nullif(age, '') as integer) >= 40
              and CAST(nullif(age, '') as integer) < 60
                then '3 - 40 to 60'
            when CAST(nullif(age, '') as integer) >= 60
                then '4 - Above 60'
            else '5 - Unknown'
        end                                 as age_group,

        gender                              as gender,

        -- Fix empty values and cast the rating to float
        CAST(nullif(clv, '') as float)      as customer_lifetime_value,

        -- Remove #DIV/0 errors, keep only 2 decimals and convert to numeric
        case
            when avg_logins is NULL
                then NULL
            when avg_logins like '%#DIV/0%'
                then NULL
            else
                round(
                   CAST(nullif( avg_logins , '') as numeric),
                   2
                )
        end as avg_logins_per_day,

        CAST(nullif(logins, '') as integer) as logins

    from source

    where
      -- Make sure that we keep only users with valid IDs
      id is NOT NULL

      -- and that we remove all the test entries
      and name NOT LIKE 'test_user_%'

)

select * from renamed
