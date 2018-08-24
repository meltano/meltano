SELECT *
FROM version.version_checks
WHERE updated_at :: DATE >= (now() - '60 days' :: INTERVAL)
      AND gitlab_version !~ '.*ee'
      AND gitlab_version !~ '.*pre'

