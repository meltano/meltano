with source as (

    select * from {{ env_var('MELTANO_LOAD_SCHEMA') }}.streams

),

renamed as (

    select
        -- Primary Key: Cast to integer and provide unique name
        CAST(id as integer) as stream_id,

        -- Foreign Keys: Cast to integer
        CAST(user_id as integer) as user_id,
        CAST(episode_id as integer) as episode_id,

        -- Cast everything else to integer
        CAST(nullif(minutes, '') as integer) as minutes_streamed,

        CAST(nullif(day, '') as integer) as day,
        CAST(nullif(month, '') as integer) as month,
        CAST(nullif(year, '') as integer) as year

    from source

    where
      -- Make sure that we keep only streams with valid IDs
      id is NOT NULL
      and user_id is NOT NULL
      and episode_id is NOT NULL

)

select * from renamed
