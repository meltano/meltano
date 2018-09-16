SELECT
 *
FROM version.usage_data
WHERE updated_at :: DATE >= (now() - '60 days' :: INTERVAL)
     AND version !~ '.*ee'
     AND version !~ '.*pre'

