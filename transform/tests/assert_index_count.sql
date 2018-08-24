WITH index AS (
    SELECT count(n.nspname) AS index_count
    FROM pg_catalog.pg_class c
      JOIN pg_catalog.pg_index i ON i.indexrelid = c.oid
      JOIN pg_catalog.pg_class c2 ON i.indrelid = c2.oid
      LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('i', '')
          AND c2.relname = 'f_opportunity'
          AND n.nspname = 'analytics'
)

SELECT *
FROM index
WHERE index_count != 4