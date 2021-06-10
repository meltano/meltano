# Data Transformation (T)

Transforms in Meltano are implemented by using [dbt](https://www.getdbt.com/). All Meltano generated projects have a `transform/` directory, which is populated with the required
configuration, models, packages, etc in order to run the transformations.

## `dbt` (Data Build Tool) Installation and Configuration

To learn more about the dbt Transformer package, please see the
[dbt plugin](https://hub.meltano.com/transformers/dbt) documentation on [Meltano Hub](https://hub.meltano.com).

## Working with Transform Plugins

`Transform` plugins are dbt packages that reside in their own repositories.

When a transform is added to a project, it is added as a dbt package in `transform/packages.yml`, enabled in `transform/dbt_project.yml`, and loaded for usage the next time dbt runs.

_**Note:** You do not have to use `transform` plugin packages in order to use DBT. Many teams instead choose to create their own custom transformations._

For more information on how to build your own dbt models or to customize your project directly, see the [dbt docs](https://docs.getdbt.com/).

### Running a Transform within your ELT pipeline

When `melatno elt` runs with the `--transform run` option, the default dbt transformations for the extractor used are run if they are installed.

As an example, assume that the following command runs:

```bash
meltano elt tap-gitlab target-postgres --transform run
```

After the Extract and Load steps are successfully completed and data have been extracted from the GitLab API and loaded to a Postgres DB, the dbt transform runs.

Meltano uses the convention that the transform has the same namespace as the extractor it is for. Transforms can be discovered and added to a Meltano project manually:

```bash
(venv) $ meltano discover transforms

transforms
tap-gitlab

(venv) $ meltano add transform tap-gitlab
Transform tap-gitlab added to your meltano.yml config
Transform tap-gitlab added to your dbt packages
Transform tap-gitlab added to your dbt_project.yml
```

### Configuring Transform Plugins

Transform plugins may have additional configuration options in `meltano.yml`. For example, the `tap-gitlab` dbt package requires three variables, which are used for
finding the tables where raw data has been loaded during the Extract-Load phase:

```yml
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "{{ env_var('PG_SCHEMA') }}.entry"
    generationmix_table: "{{ env_var('PG_SCHEMA') }}.generationmix"
    region_table: "{{ env_var('PG_SCHEMA') }}.region"
```

As an alternative to providing values from environment variables, you can also set values directly in `meltano.yml`:

```yml
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "my_raw_schema.entry"
    generationmix_table: "my_raw_schema.generationmix"
    region_table: "my_raw_schema.region"
```

Whenever Meltano runs a new transformation, `transform/dbt_project.yml` is updated using the values provided in `meltano.yml`.
