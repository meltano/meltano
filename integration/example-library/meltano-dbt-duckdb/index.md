# Get setup

This example shows how to build a local pipeline with `tap-smoke-test`, [`meltano-map-transformer`](https://github.com/MeltanoLabs/meltano-map-transform), `target-duckdb` and dbt v2 (`dbt-duckdb`).
To get started with this example download the [meltano yml](/integration/example-library/meltano-dbt-duckdb/meltano.yml) and [animals-data.ndjson](/integration/example-library/meltano-dbt-duckdb/animals-data.ndjson) to a fresh directory and run:

```shell
meltano install
mkdir -p output
```

## Extract, map and load

`tap-smoke-test` reads the records in `animals-data.ndjson`, the `animals-subset` mapping keeps only a handful of fields and declares `id` as the primary key, and `target-duckdb` writes the result to `output/warehouse.duckdb`:

```shell
meltano config list tap-smoke-test
meltano run tap-smoke-test animals-subset target-duckdb
```

## Getting dbt v2 involved

The `meltano.yml` didn't include dbt, so let's add the `dbt-duckdb` utility from a plugin definition reference:

```shell
meltano add utility dbt-duckdb --from-ref https://raw.githubusercontent.com/meltano/hub/refs/heads/dbt-v2/_data/meltano/utilities/dbt-duckdb/dbt-labs.yml
```

### Prep the dbt project

```shell
meltano invoke dbt-duckdb:initialize
mkdir -p ./transform/models/tap_smoke_test
```

```shell
tee ./transform/models/tap_smoke_test/source.yml << END
version: 2
sources:
  - name: tap_smoke_test
    schema: raw
    tables:
      - name: animals
END
```

### Add a demo model

```shell
tee ./transform/models/tap_smoke_test/verified_animals.sql << END
{{
  config(
    materialized='table'
  )
}}

select id, description, views
from {{ source('tap_smoke_test', 'animals') }}
where verified
END
```

```shell
tee ./transform/models/tap_smoke_test/schema.yml << END
version: 2
models:
  - name: verified_animals
    columns:
      - name: id
        data_tests:
          - unique
          - not_null
END
```

# Pulling it all together

Build the model first, then test it:

```shell
meltano run tap-smoke-test animals-subset target-duckdb dbt-duckdb:run dbt-duckdb:test
```
