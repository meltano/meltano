---
description: Learn how to transform your loaded data for analysis using Meltano and dbt.
lastUpdatedSignificantly: 2020-02-20
---

# Data Transformation (T)

Transforms in Meltano are implemented by using [dbt](https://www.getdbt.com/). All Meltano generated projects have a `transform/` directory, which is populated with the required configuration, models, packages, etc in order to run the transformations.

When Meltano elt runs with the `--transform run` option, the default dbt transformations for the extractor used are run if they are installed; but Meltano will **never** modify the original source file.

As an example, assume that the following command runs:

```
meltano elt tap-gitlab target-postgres --transform run
```

After the Extract and Load steps are successfully completed and data have been extracted from the GitLab API and loaded to a Postgres DB, the dbt transform runs.

Meltano uses the convention that the transform has the same namespace as the extractor it is for. Transforms can be discovered and added to a Meltano project manually:

```
(venv) $ meltano discover transforms

transforms
tap-gitlab

(venv) $ meltano add transform tap-gitlab
Transform tap-gitlab added to your meltano.yml config
Transform tap-gitlab added to your dbt packages
Transform tap-gitlab added to your dbt_project.yml
```

Transforms are basically dbt packages that reside in their own repositories. If you want to see in more details how such a package can be defined, you can check the dbt documentation on [Package Management](https://docs.getdbt.com/docs/package-management) and [dbt-tap-gitlab](https://gitlab.com/meltano/dbt-tap-gitlab), the project used for defining the default transforms for `tap-gitlab`.

When a transform is added to a project, it is added as a dbt package in `transform/packages.yml`, enabled in `transform/dbt_project.yml`, and loaded for usage the next time dbt runs.

The format of the `meltano.yml` entries for transforms can have additional parameters. For example, the `tap-gitlab` dbt package requires three variables, which are used for finding the tables where the raw Carbon Intensity data have been loaded during the Extract-Load phase:

```
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "{{ env_var('PG_SCHEMA') }}.entry"
    generationmix_table: "{{ env_var('PG_SCHEMA') }}.generationmix"
    region_table: "{{ env_var('PG_SCHEMA') }}.region"
```

Those entries may follow dbt's syntax in order to fetch values from environment variables. In this case, $PG_SCHEMA must be available in order for the transformations to know in which Postgres schema to find the tables with the Carbon Intensity data. Meltano uses $PG_SCHEMA by default as it is the same default schema also used by the Postgres Loader.

You can keep those parameters as they are and provide the schema as an environment variable or set the schema manually in `meltano.yml`:

```
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "my_raw_schema.entry"
    generationmix_table: "my_raw_schema.generationmix"
    region_table: "my_raw_schema.region"
```

When Meltano runs a new transformation, `transform/dbt_project.yml` is always kept up to date with whatever is provided in `meltano.yml`.

Finally, dbt can be configured by updating `transform/profile/profiles.yml`. By default, Meltano sets up dbt to use the same database and user as the Postgres Loader and store the results of the transformations in the `analytics` schema.
