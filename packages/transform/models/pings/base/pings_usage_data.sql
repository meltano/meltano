WITH source as (

    SELECT *
    FROM version.usage_data
)

SELECT *
FROM source
WHERE uuid IS NOT NULL