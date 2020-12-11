with source as (

    select * from {{ env_var('MELTANO_LOAD_SCHEMA') }}.episodes

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer) as episode_id,

        -- Keep the Episode Number as a string
        no as episode_number,
        title as title,
        tv_series as tv_series,

         -- Fix empty values and cast the rating to float
        CAST(nullif(rating, '') as float) as imdb_rating,

        -- Remove the $ from the start and the commas
        --  and then cast to float
        CAST(
            nullif( replace( substring(ad_rev from 2), ',', ''),'' )
            AS float
        ) as ad_revenue_per_minute

    from source

    where
      -- Make sure that we keep only episodes with valid IDs
      id is NOT NULL

      -- and that we remove all the test entries
      and title NOT LIKE 'test_the_test_%'

)

select * from renamed
