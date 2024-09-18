---
title: Meltano 2.0 Migration Guide
description: Migrate existing "v1" projects to the latest version of Meltano
layout: doc
redirect_from:
  - /reference/v2-migration/
sidebar_position: 20
---

_Note: This document is still a work in progress. Expect further changes, coming soon._

The following list includes all recommended migration tasks as well as breaking changes in Meltano version 2.0.

## Recommended

### Migrate to an Adapter-Specific `dbt` Transformer

If you previously used `dbt` or `dbt-<adapter>` ([available adapters documentation](https://docs.getdbt.com/docs/available-adapters)) Transformer, we recommend migrating to an adapter specific [utility plugin](https://hub.meltano.com/utilities/).

#### Install `dbt`

This is easy to do! Following the instructions from above to discover and install your chosen adapter:

```bash
# install adapter-specific dbt, e.g. for snowflake
meltano add utility dbt-snowflake
```

#### Update your `dbt_project.yml`

Installation of a new Transformer will introduce two important files to your `transform/` directory:

- A new `profiles.yml` file in `transform/profiles/<adapter name>/profiles.yml`
- A new `dbt_project.yml` file in `transform/dbt_project (<adapter name>).yml`

The new `profiles.yml` will only be used by adapter-specific `dbt` executions (e.g. `dbt-snowflake`), and can be customized to meet your requirements.
Your existing `profiles.yml` will remain in use by your existing `dbt` Transformer plugin (via `elt` and `invoke`).

It is likely that the new `dbt_project (<adapter name>).yml` will contain changes from your previous `dbt_project.yml` file, especially if you haven't already upgraded to [`dbt` v1.0](https://docs.getdbt.com/guides/migration/versions/upgrading-to-v1.0).
To complete your migration, consolidate `dbt_project.yml` and `dbt_project (<adapter name>).yml` into a single file called `dbt_project.yml`.
As this project file will be used by both `dbt` and `dbt-<adapter>` Transformer plugins by default, you must ensure you are running an up-to-date installation of plugin `dbt` if you intend to use both adapter-specific and legacy `dbt` installs together (not recommended).

If you make use of [Transform](/guide/transformation) plugins, these will continue to work as regular `dbt` packages. However adding new Transform plugins will currently (tracking at [#3304](https://github.com/meltano/meltano/issues/3304)) re-add the legacy `dbt` Transformer plugin.
To avoid this we recommend adding Transforms as regular packages directly via dbt as per the [`dbt` Packages documentation](https://docs.getdbt.com/docs/building-a-dbt-project/package-management).

#### Remove the `dbt` Transformer plugin and associated files

To remove the legacy `dbt` Transformer plugin, run:

```bash
# remove the transformer `dbt`
meltano remove transformer dbt

# remove the file bundle `dbt`
meltano remove files dbt
```

Removing a file bundle _does not_ remove any files from your `transform/` directory.
Manually remove `transform/profile/profiles.yml` to complete clean-up (as adapter-specific installs come with their own `profiles.yml` in `transform/profiles/<adapter name>/profiles.yml`).

### Migrate from orchestrators to utilities

If you have been using Meltano orchestrators to schedule your ELT jobs, we recommend migrating to the new [utilities](https://hub.meltano.com/utilities/):

- [Airflow](https://hub.meltano.com/utilities/airflow)
- [Dagster](https://hub.meltano.com/utilities/dagster)

## Removed

### `model` and `dashboard` plugin types

These plugin types provided very basic BI capabilities using Meltano UI. However there are already great 3rd party open source BI solutions in this space, such as the newly added Superset plugin.
Meltano `model` and `dashboard` plugins have been removed in favour of existing and future 3rd party tools for the same purpose.

### `transform` support in `meltano elt`

Meltano 2.0 continues to support extract-load (EL) operations with `meltano elt`. However, for EL+T operations which also need to transform data, please use `meltano run`.

### `transform` support in Meltano schedules

Meltano 2.0 continues to support extract-load (EL) operations in schedules.
However, for EL+T operations which also need to transform data, please use the new `meltano job add` [command](/reference/command-line-interface#job) to create a job definition and then specify the new job name in your schedule.

### `env_aliases` in Plugin config

As part of our effort to streamline the configuration experience in Meltano, we are deprecating the `env_aliases` attribute of plugin definitions.
Previously `env_aliases` provided two functions:

1. Sourcing setting values from the terminal by a name other than the default environment variable (of the form `<PLUGIN_NAME>_<SETTING_NAME>`).
1. Writing setting values into the plugins' runtime environment under an environment variable name other than the default.

For sourcing setting values we encourage users going forward to make use of the default environment variables (of the form `<PLUGIN_NAME>_<SETTING_NAME>`) for settings in most cases.
These can be conveniently found for a given plugin by running `meltano config <plugin> list`.
In cases where an environment variable of a name other than the default must be used to source a setting value, Meltano supports referencing in `meltano.yml`.
For example:

```yaml
plugins:
  extractors:
    - name: tap-gitlab
      config:
        ultimate_license: $GITLAB_API_ULTIMATE_LICENSE
```

This will take the value from the environment variable `GITLAB_API_ULTIMATE_LICENSE` and use it configure the `tap-gitlab` setting named `ultimate_license`.

For writing setting values into the plugins' runtime environment under an environment variable name other than the default, we support the `env:` key for setting definitions.
These can be added or overridden in your `meltano.yml` file. For example:

```yaml
plugins:
  extractors:
    - name: tap-gitlab
      settings:
        - name: ultimate_license
          env: GITLAB_API_ULTIMATE_LICENSE
```

This will create an environment variable called `GITLAB_API_ULTIMATE_LICENSE` in the plugins' runtime environment with the configured value of the setting `ultimate_license`.

#### Updating your Project

Before v2.0 Meltano made use of `env_aliases` internally and in several common plugins.
To ensure Meltano and those plugins continue to work as expected, references to the deprecated environment variables in your own project should be replaced.
The table below contains details of the `env_aliases` that have been removed, and the corresponding default setting environment variable to use in each case.
If for any reason you wish to keep sourcing or writing setting values to deprecated aliases, we recommend using the techniques detailed above to replace the functionality formally provided by `env_aliases`.

<table>
  <tr>
    <td>Plugin</td>
    <td>Variant</td>
    <td>Deprecated</td>
    <td>Replacement</td>
  </tr>
  <tr>
    <td rowspan="18">meltano</td>
    <td rowspan="18"></td>
    <td>MELTANO_LOG_LEVEL</td>
    <td>MELTANO_CLI_LOG_LEVEL</td>
  </tr>
  <tr>
    <td>MELTANO_LOG_CONFIG</td>
    <td>MELTANO_CLI_LOG_CONFIG</td>
  </tr>
  <tr>
    <td>MELTANO_API_HOSTNAME</td>
    <td>MELTANO_UI_BIND_HOST</td>
  </tr>
  <tr>
    <td>MELTANO_API_PORT</td>
    <td>MELTANO_UI_BIND_PORT</td>
  </tr>
  <tr>
    <td>PORT</td>
    <td>MELTANO_UI_BIND_PORT</td>
  </tr>
  <tr>
    <td>WORKERS</td>
    <td>MELTANO_UI_WORKERS</td>
  </tr>
  <tr>
    <td>WEB_CONCURRENCY</td>
    <td>MELTANO_UI_WORKERS</td>
  </tr>
  <tr>
    <td>FORWARDED_ALLOW_IPS</td>
    <td>MELTANO_UI_FORWARDED_ALLOW_IPS</td>
  </tr>
  <tr>
    <td>MELTANO_READONLY</td>
    <td>MELTANO_UI_READONLY</td>
  </tr>
  <tr>
    <td>MELTANO_AUTHENTICATION</td>
    <td>MELTANO_UI_AUTHENTICATION</td>
  </tr>
  <tr>
    <td>MELTANO_NOTIFICATION</td>
    <td>MELTANO_UI_NOTIFICATION</td>
  </tr>
  <tr>
    <td>TAP_ADWORDS_OAUTH_CLIENT_ID</td>
    <td>MELTANO_OAUTH_SERVICE_GOOGLE_ADWORDS_CLIENT_ID</td>
  </tr>
  <tr>
    <td>TAP_ADWORDS_OAUTH_CLIENT_SECRET</td>
    <td>MELTANO_OAUTH_SERVICE_GOOGLE_ADWORDS_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>OAUTH_GITLAB_APPLICATION_ID</td>
    <td>MELTANO_OAUTH_GITLAB_CLIENT_ID</td>
  </tr>
  <tr>
    <td>OAUTH_GITLAB_SECRET</td>
    <td>MELTANO_OAUTH_GITLAB_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>MELTANO_CLI_TRACKING_ID</td>
    <td>MELTANO_TRACKING_IDS_CLI</td>
  </tr>
  <tr>
    <td>MELTANO_UI_TRACKING_ID</td>
    <td>MELTANO_TRACKING_IDS_UI</td>
  </tr>
  <tr>
    <td>MELTANO_EMBED_TRACKING_ID</td>
    <td>MELTANO_TRACKING_IDS_UI_EMBED</td>
  </tr>
  <tr>
    <td>dbt-bigquery</td>
    <td>meltano</td>
    <td>DBT_PROFILES_DIR</td>
    <td>DBT_BIGQUERY_PROFILES_DIR</td>
  </tr>
  <tr>
    <td>dbt-postgres</td>
    <td>meltano</td>
    <td>DBT_PROFILES_DIR</td>
    <td>DBT_POSTGRES_PROFILES_DIR</td>
  </tr>
  <tr>
    <td>dbt-redshift</td>
    <td>meltano</td>
    <td>DBT_PROFILES_DIR</td>
    <td>DBT_REDSHIFT_PROFILES_DIR</td>
  </tr>
  <tr>
    <td>dbt-snowflake</td>
    <td>meltano</td>
    <td>DBT_PROFILES_DIR</td>
    <td>DBT_SNOWFLAKE_PROFILES_DIR</td>
  </tr>
  <tr>
    <td rowspan="6">tap-adwords</td>
    <td rowspan="3">meltano</td>
    <td>OAUTH_GOOGLE_ADWORDS_CLIENT_ID</td>
    <td>TAP_ADWORDS_OAUTH_CLIENT_ID</td>
  </tr>
  <tr>
    <td>OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET</td>
    <td>TAP_ADWORDS_OAUTH_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN</td>
    <td>TAP_ADWORDS_DEVELOPER_TOKEN</td>
  </tr>
  <tr>
    <td rowspan="3">singer-io</td>
    <td>OAUTH_GOOGLE_ADWORDS_CLIENT_ID</td>
    <td>TAP_ADWORDS_OAUTH_CLIENT_ID</td>
  </tr>
  <tr>
    <td>OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET</td>
    <td>TAP_ADWORDS_OAUTH_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>OAUTH_GOOGLE_ADWORDS_DEVELOPER_TOKEN</td>
    <td>TAP_ADWORDS_DEVELOPER_TOKEN</td>
  </tr>
  <tr>
    <td>tap-bigquery</td>
    <td>anelendata</td>
    <td>GOOGLE_APPLICATION_CREDENTIALS</td>
    <td>TAP_BIGQUERY_CREDENTIALS_PATH</td>
  </tr>
  <tr>
    <td rowspan="3">tap-bing-ads</td>
    <td rowspan="3">singer-io</td>
    <td>OAUTH_BING_ADS_CLIENT_ID</td>
    <td>TAP_BING_ADS_OAUTH_CLIENT_ID</td>
  </tr>
  <tr>
    <td>OAUTH_BING_ADS_CLIENT_SECRET</td>
    <td>TAP_BING_ADS_OAUTH_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>OAUTH_BING_ADS_DEVELOPER_TOKEN</td>
    <td>TAP_BING_ADS_DEVELOPER_TOKEN</td>
  </tr>
  <tr>
    <td rowspan="2">tap-csv</td>
    <td>meltano</td>
    <td>TAP_CSV_FILES_DEFINITION</td>
    <td>TAP_CSV_CSV_FILES_DEFINITION</td>
  </tr>
  <tr>
    <td>meltanolabs</td>
    <td>TAP_CSV_FILES_DEFINITION</td>
    <td>TAP_CSV_CSV_FILES_DEFINITION</td>
  </tr>
  <tr>
    <td rowspan="10">tap-gitlab</td>
    <td rowspan="5">meltano</td>
    <td>GITLAB_API_GROUPS</td>
    <td>TAP_GITLAB_GROUPS</td>
  </tr>
  <tr>
    <td>GITLAB_API_PROJECTS</td>
    <td>TAP_GITLAB_PROJECTS</td>
  </tr>
  <tr>
    <td>GITLAB_API_START_DATE</td>
    <td>TAP_GITLAB_START_DATE</td>
  </tr>
  <tr>
    <td>GITLAB_API_TOKEN</td>
    <td>TAP_GITLAB_PRIVATE_TOKEN</td>
  </tr>
  <tr>
    <td>GITLAB_API_ULTIMATE_LICENSE</td>
    <td>TAP_GITLAB_ULTIMATE_LICENSE</td>
  </tr>
  <tr>
    <td rowspan="5">meltanolabs</td>
    <td>GITLAB_API_GROUPS</td>
    <td>TAP_GITLAB_GROUPS</td>
  </tr>
  <tr>
    <td>GITLAB_API_PROJECTS</td>
    <td>TAP_GITLAB_PROJECTS</td>
  </tr>
  <tr>
    <td>GITLAB_API_START_DATE</td>
    <td>TAP_GITLAB_START_DATE</td>
  </tr>
  <tr>
    <td>GITLAB_API_TOKEN</td>
    <td>TAP_GITLAB_PRIVATE_TOKEN</td>
  </tr>
  <tr>
    <td>GITLAB_API_ULTIMATE_LICENSE</td>
    <td>TAP_GITLAB_ULTIMATE_LICENSE</td>
  </tr>
  <tr>
    <td rowspan="9">tap-google-analytics</td>
    <td rowspan="9">meltano</td>
    <td>GOOGLE_ANALYTICS_API_CLIENT_SECRETS</td>
    <td>TAP_GOOGLE_ANALYTICS_KEY_FILE_LOCATION</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_END_DATE</td>
    <td>TAP_GOOGLE_ANALYTICS_END_DATE</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_OAUTH_ACCESS_TOKEN</td>
    <td>TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_ACCESS_TOKEN</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_OAUTH_CLIENT_ID</td>
    <td>TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_ID</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_OAUTH_CLIENT_SECRET</td>
    <td>TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_OAUTH_REFRESH_TOKEN</td>
    <td>TAP_GOOGLE_ANALYTICS_OAUTH_CREDENTIALS_REFRESH_TOKEN</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_REPORTS</td>
    <td>TAP_GOOGLE_ANALYTICS_REPORTS</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_START_DATE</td>
    <td>TAP_GOOGLE_ANALYTICS_START_DATE</td>
  </tr>
  <tr>
    <td>GOOGLE_ANALYTICS_API_VIEW_ID</td>
    <td>TAP_GOOGLE_ANALYTICS_VIEW_ID</td>
  </tr>
  <tr>
    <td>tap-pendo</td>
    <td>singer-io</td>
    <td>TAP_PENDO_INTEGRATION_KEY</td>
    <td>TAP_PENDO_X_PENDO_INTEGRATION_KEY</td>
  </tr>
  <tr>
    <td rowspan="5">tap-stripe</td>
    <td rowspan="2">meltano</td>
    <td>STRIPE_ACCOUNT_ID</td>
    <td>TAP_STRIPE_ACCOUNT_ID</td>
  </tr>
  <tr>
    <td>STRIPE_API_KEY</td>
    <td>TAP_STRIPE_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>prratek</td>
    <td>STRIPE_API_KEY</td>
    <td>TAP_STRIPE_API_KEY</td>
  </tr>
  <tr>
    <td rowspan="2">singer-io</td>
    <td>STRIPE_ACCOUNT_ID</td>
    <td>TAP_STRIPE_ACCOUNT_ID</td>
  </tr>
  <tr>
    <td>STRIPE_API_KEY</td>
    <td>TAP_STRIPE_CLIENT_SECRET</td>
  </tr>
  <tr>
    <td>target-bigquery</td>
    <td>adswerve</td>
    <td>GOOGLE_APPLICATION_CREDENTIALS</td>
    <td>TARGET_BIGQUERY_CREDENTIALS_PATH</td>
  </tr>
  <tr>
    <td rowspan="37">target-postgres</td>
    <td rowspan="17">datamill-co</td>
    <td>PG_ADDRESS</td>
    <td>TARGET_POSTGRES_POSTGRES_HOST</td>
  </tr>
  <tr>
    <td>PG_DATABASE</td>
    <td>TARGET_POSTGRES_POSTGRES_DATABASE</td>
  </tr>
  <tr>
    <td>PG_PASSWORD</td>
    <td>TARGET_POSTGRES_POSTGRES_PASSWORD</td>
  </tr>
  <tr>
    <td>PG_PORT</td>
    <td>TARGET_POSTGRES_POSTGRES_PORT</td>
  </tr>
  <tr>
    <td>PG_SCHEMA</td>
    <td>TARGET_POSTGRES_POSTGRES_SCHEMA</td>
  </tr>
  <tr>
    <td>PG_USERNAME</td>
    <td>TARGET_POSTGRES_POSTGRES_USERNAME</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_DATABASE</td>
    <td>TARGET_POSTGRES_POSTGRES_DATABASE</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_HOST</td>
    <td>TARGET_POSTGRES_POSTGRES_HOST</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_PASSWORD</td>
    <td>TARGET_POSTGRES_POSTGRES_PASSWORD</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_PORT</td>
    <td>TARGET_POSTGRES_POSTGRES_PORT</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SCHEMA</td>
    <td>TARGET_POSTGRES_POSTGRES_SCHEMA</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SSLCERT</td>
    <td>TARGET_POSTGRES_POSTGRES_SSLCERT</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SSLCRL</td>
    <td>TARGET_POSTGRES_POSTGRES_SSLCRL</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SSLKEY</td>
    <td>TARGET_POSTGRES_POSTGRES_SSLKEY</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SSLMODE</td>
    <td>TARGET_POSTGRES_POSTGRES_SSLMODE</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_SSLROOTCERT</td>
    <td>TARGET_POSTGRES_POSTGRES_SSLROOTCERT</td>
  </tr>
  <tr>
    <td>TARGET_POSTGRES_USERNAME</td>
    <td>TARGET_POSTGRES_POSTGRES_USERNAME</td>
  </tr>
  <tr>
    <td rowspan="14">meltano</td>
    <td>PG_ADDRESS</td>
    <td>TARGET_POSTGRES_HOST</td>
  </tr>
  <tr>
    <td>PG_DATABASE</td>
    <td>TARGET_POSTGRES_DBNAME</td>
  </tr>
  <tr>
    <td>PG_PASSWORD</td>
    <td>TARGET_POSTGRES_PASSWORD</td>
  </tr>
  <tr>
    <td>PG_PORT</td>
    <td>TARGET_POSTGRES_PORT</td>
  </tr>
  <tr>
    <td>PG_SCHEMA</td>
    <td>TARGET_POSTGRES_SCHEMA</td>
  </tr>
  <tr>
    <td>PG_URL</td>
    <td>TARGET_POSTGRES_URL</td>
  </tr>
  <tr>
    <td>PG_USERNAME</td>
    <td>TARGET_POSTGRES_USER</td>
  </tr>
  <tr>
    <td>POSTGRES_DBNAME</td>
    <td>TARGET_POSTGRES_DBNAME</td>
  </tr>
  <tr>
    <td>POSTGRES_HOST</td>
    <td>TARGET_POSTGRES_HOST</td>
  </tr>
  <tr>
    <td>POSTGRES_PASSWORD</td>
    <td>TARGET_POSTGRES_PASSWORD</td>
  </tr>
  <tr>
    <td>POSTGRES_PORT</td>
    <td>TARGET_POSTGRES_PORT</td>
  </tr>
  <tr>
    <td>POSTGRES_SCHEMA</td>
    <td>TARGET_POSTGRES_SCHEMA</td>
  </tr>
  <tr>
    <td>POSTGRES_URL</td>
    <td>TARGET_POSTGRES_URL</td>
  </tr>
  <tr>
    <td>POSTGRES_USER</td>
    <td>TARGET_POSTGRES_USER</td>
  </tr>
  <tr>
    <td rowspan="6">transferwise</td>
    <td>PG_ADDRESS</td>
    <td>TARGET_POSTGRES_HOST</td>
  </tr>
  <tr>
    <td>PG_DATABASE</td>
    <td>TARGET_POSTGRES_DBNAME</td>
  </tr>
  <tr>
    <td>PG_PASSWORD</td>
    <td>TARGET_POSTGRES_PASSWORD</td>
  </tr>
  <tr>
    <td>PG_PORT</td>
    <td>TARGET_POSTGRES_PORT</td>
  </tr>
  <tr>
    <td>PG_SCHEMA</td>
    <td>TARGET_POSTGRES_DEFAULT_TARGET_SCHEMA</td>
  </tr>
  <tr>
    <td>PG_USERNAME</td>
    <td>TARGET_POSTGRES_USER</td>
  </tr>
  <tr>
    <td rowspan="5">target-redshift</td>
    <td rowspan="5">transferwise</td>
    <td>AWS_ACCESS_KEY_ID</td>
    <td>TARGET_REDSHIFT_AWS_ACCESS_KEY_ID</td>
  </tr>
  <tr>
    <td>AWS_PROFILE</td>
    <td>TARGET_REDSHIFT_AWS_PROFILE</td>
  </tr>
  <tr>
    <td>AWS_SECRET_ACCESS_KEY</td>
    <td>TARGET_REDSHIFT_AWS_SECRET_ACCESS_KEY</td>
  </tr>
  <tr>
    <td>AWS_SESSION_TOKEN</td>
    <td>TARGET_REDSHIFT_AWS_SESSION_TOKEN</td>
  </tr>
  <tr>
    <td>TARGET_REDSHIFT_SCHEMA</td>
    <td>TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA</td>
  </tr>
  <tr>
    <td rowspan="39">target-snowflake</td>
    <td rowspan="15">datamill-co</td>
    <td>SF_ACCOUNT</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_ACCOUNT</td>
  </tr>
  <tr>
    <td>SF_DATABASE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_DATABASE</td>
  </tr>
  <tr>
    <td>SF_PASSWORD</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_PASSWORD</td>
  </tr>
  <tr>
    <td>SF_ROLE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_ROLE</td>
  </tr>
  <tr>
    <td>SF_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_SCHEMA</td>
  </tr>
  <tr>
    <td>SF_USER</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_USERNAME</td>
  </tr>
  <tr>
    <td>SF_WAREHOUSE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_WAREHOUSE</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_ACCOUNT</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_ACCOUNT</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_DATABASE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_DATABASE</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_PASSWORD</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_PASSWORD</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_ROLE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_ROLE</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_SCHEMA</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_USERNAME</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_USERNAME</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_USERNAME</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_USERNAME</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_WAREHOUSE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_WAREHOUSE</td>
  </tr>
  <tr>
    <td rowspan="14">meltano</td>
    <td>SF_ACCOUNT</td>
    <td>TARGET_SNOWFLAKE_ACCOUNT</td>
  </tr>
  <tr>
    <td>SF_DATABASE</td>
    <td>TARGET_SNOWFLAKE_DATABASE</td>
  </tr>
  <tr>
    <td>SF_PASSWORD</td>
    <td>TARGET_SNOWFLAKE_PASSWORD</td>
  </tr>
  <tr>
    <td>SF_ROLE</td>
    <td>TARGET_SNOWFLAKE_ROLE</td>
  </tr>
  <tr>
    <td>SF_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_SCHEMA</td>
  </tr>
  <tr>
    <td>SF_USER</td>
    <td>TARGET_SNOWFLAKE_USERNAME</td>
  </tr>
  <tr>
    <td>SF_WAREHOUSE</td>
    <td>TARGET_SNOWFLAKE_WAREHOUSE</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_ACCOUNT</td>
    <td>TARGET_SNOWFLAKE_ACCOUNT</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_DATABASE</td>
    <td>TARGET_SNOWFLAKE_DATABASE</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_PASSWORD</td>
    <td>TARGET_SNOWFLAKE_PASSWORD</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_ROLE</td>
    <td>TARGET_SNOWFLAKE_ROLE</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_SCHEMA</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_USERNAME</td>
    <td>TARGET_SNOWFLAKE_USERNAME</td>
  </tr>
  <tr>
    <td>SNOWFLAKE_WAREHOUSE</td>
    <td>TARGET_SNOWFLAKE_WAREHOUSE</td>
  </tr>
  <tr>
    <td rowspan="10">transferwise</td>
    <td>SF_ACCOUNT</td>
    <td>TARGET_SNOWFLAKE_ACCOUNT</td>
  </tr>
  <tr>
    <td>SF_DATABASE</td>
    <td>TARGET_SNOWFLAKE_DBNAME</td>
  </tr>
  <tr>
    <td>SF_PASSWORD</td>
    <td>TARGET_SNOWFLAKE_PASSWORD</td>
  </tr>
  <tr>
    <td>SF_ROLE</td>
    <td>TARGET_SNOWFLAKE_SNOWFLAKE_ROLE</td>
  </tr>
  <tr>
    <td>SF_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA</td>
  </tr>
  <tr>
    <td>SF_USER</td>
    <td>TARGET_SNOWFLAKE_USER</td>
  </tr>
  <tr>
    <td>SF_WAREHOUSE</td>
    <td>TARGET_SNOWFLAKE_WAREHOUSE</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_DATABASE</td>
    <td>TARGET_SNOWFLAKE_DBNAME</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_SCHEMA</td>
    <td>TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA</td>
  </tr>
  <tr>
    <td>TARGET_SNOWFLAKE_USERNAME</td>
    <td>TARGET_SNOWFLAKE_USER</td>
  </tr>
  <tr>
    <td rowspan="2">target-sqlite</td>
    <td>meltano</td>
    <td>SQLITE_DATABASE</td>
    <td>TARGET_SQLITE_DATABASE</td>
  </tr>
  <tr>
    <td>meltanolabs</td>
    <td>SQLITE_DATABASE</td>
    <td>TARGET_SQLITE_DATABASE</td>
  </tr>
</table>

## CLI and API Changes

#### Use `--state-id` instead of `--job_id`

In 2.0, many references to "Job ID" in our code and docs were changed to the more accurate name of "State ID".

If you are explicitly providing a `--job_id` option to any scripted or otherwise automated CLI workflows, these commands should be updated to use the `--state-id` option instead.

#### Schedule list format changes

If you have custom orchestrator integrations based on the `meltano schedule list` command, you will need to make adjustments to handle a new output format.

With the addition of support for scheduled jobs in 2.0, the schema output of `meltano schedule list --format=json` has changed.
It now includes a top level field `schedules` and two nested array fields `job` and `elt` which hold and describe their respective schedules.

ex:

```json
{
  "schedules": {
    "job": [
      {
        "name": "daily-doit",
        "interval": "@daily",
        "cron_interval": "0 0 * * *",
        "env": {},
        "job": {
          "name": "simple-demo",
          "tasks": [
            "tap-gitlab hide-gitlab-secrets target-jsonl",
            "tap-gitlab target-csv"
          ]
        }
      }
    ],
    "elt": [
      {legacy elt schedule entry remains unchanged}, ...
    ]
  }
}
```
