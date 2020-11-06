---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into Snowflake
---

# Snowflake

The `target-snowflake` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into a [Snowflake](https://www.snowflake.com/) data warehouse.

To learn more about `target-snowflake`, refer to the repository at <https://github.com/datamill-co/target-snowflake>.

#### Alternative variants

Multiple [variants](/docs/plugins.html#variants) of `target-snowflake` are available.
This document describes the default `datamill-co` variant, which is recommended for new users.

Alternative options are [`transferwise`](./snowflake--transferwise.html) and [`meltano`](./snowflake--meltano.html).

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `target-snowflake` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-snowflake
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the "Add to project" button for "Snowflake".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

## Settings

`target-snowflake` requires the [configuration](/docs/configuration.html) of the following settings:

- [Snowflake Account](#snowflake-account)
- [Snowflake Username](#snowflake-username)
- [Snowflake Password](#snowflake-password)
- [Snowflake Database](#snowflake-database)
- [Snowflake Warehouse](#snowflake-warehouse)
- [Snowflake Schema](#snowflake-schema)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-snowflake` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{6-11}
plugins:
  loaders:
  - name: target-snowflake
    variant: datamill-co
    pip_url: target-snowflake
    config:
      snowflake_account: my_account
      snowflake_username: MY_USER
      snowflake_database: MY_DATABASE
      snowflake_warehouse: MY_WAREHOUSE
      # snowflake_schema: MY_SCHEMA     # override if default (see below) is not appropriate
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_SNOWFLAKE_PASSWORD=my_password
```

### Snowflake Account

- Name: `snowflake_account`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_ACCOUNT`, alias: `SF_ACCOUNT`

You can find your account name in your Snowflake URL: `https://<account>.snowflakecomputing.com`.

It might require the `region` and `cloud` platform where your account is located, in the form of: `<your_account_name>.<region_id>.<cloud>` (e.g. `xy12345.east-us-2.azure`)

See <https://docs.snowflake.net/manuals/user-guide/connecting.html#your-snowflake-account-name-and-url>.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_account <account>

export TARGET_SNOWFLAKE_ACCOUNT=<account>
```

### Snowflake Username

- Name: `snowflake_username`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_USERNAME`, alias: `SF_USER`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_username <username>

export TARGET_SNOWFLAKE_USERNAME=<username>
```

### Snowflake Password

- Name: `snowflake_password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PASSWORD`, alias: `SF_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_password <password>

export TARGET_SNOWFLAKE_PASSWORD=<password>
```

### Snowflake Role

- Name: `snowflake_role`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_ROLE`, alias: `SF_ROLE`

If not specified, Snowflake will use the user's default role.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_role <role>

export TARGET_SNOWFLAKE_ROLE=<role>
```

### Snowflake Database

- Name: `snowflake_database`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DATABASE`, alias: `SF_DATABASE`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_database <database>

export TARGET_SNOWFLAKE_DATABASE=<database>
```

### Snowflake Authenticator

- Name: `snowflake_authenticator`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_AUTHENTICATOR`
- Default: `snowflake`

Specifies the authentication provider for snowflake to use. Valud options are the internal one (`snowflake`), a browser session (`externalbrowser`), or Okta (`https://<your_okta_account_name>.okta.com`). See the snowflake docs for more details.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_authenticator externalbrowser

export TARGET_SNOWFLAKE_AUTHENTICATOR=externalbrowser
```

### Snowflake Schema

- Name: `snowflake_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_SCHEMA`, alias: `SF_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html). Values are automatically converted to uppercase before they're passed on to the plugin, so `tap_gitlab` becomes `TAP_GITLAB`.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_schema <schema>

export TARGET_SNOWFLAKE_SCHEMA=<schema>
```

### Snowflake Warehouse

- Name: `snowflake_warehouse`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_WAREHOUSE`, alias: `SF_WAREHOUSE`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set snowflake_warehouse <warehouse>

export TARGET_SNOWFLAKE_WAREHOUSE=<warehouse>
```

### Invalid Records Detect

- Name: `invalid_records_detect`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_INVALID_RECORDS_DETECT`
- Default: `true`

Include `false` in your config to disable crashing on invalid records.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set invalid_records_detect false

export TARGET_SNOWFLAKE_INVALID_RECORDS_DETECT=false
```

### Invalid Records Threshold

- Name: `invalid_records_threshold`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_INVALID_RECORDS_THRESHOLD`
- Default: `0`

Include a positive value `n` in your config to allow at most `n` invalid records per stream before giving up.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set invalid_records_threshold 5

export TARGET_SNOWFLAKE_INVALID_RECORDS_THRESHOLD=5
```

### Disable Collection

- Name: `disable_collection`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DISABLE_COLLECTION`
- Default: `false`

Include `true` in your config to disable [Singer Usage Logging](https://github.com/datamill-co/target-snowflake#usage-logging).

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set disable_collection true

export TARGET_SNOWFLAKE_DISABLE_COLLECTION=true
```

### Logging Level

- Name: `logging_level`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_LOGGING_LEVEL`
- Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Default: `INFO`

The level for logging. Set to `DEBUG` to get things like queries executed, timing of those queries, etc. See [Python's Logger Levels](https://docs.python.org/3/library/logging.html#levels) for information about valid values.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set logging_level DEBUG

export TARGET_SNOWFLAKE_LOGGING_LEVEL=DEBUG
```

### Persist Empty Tables

- Name: `persist_empty_tables`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PERSIST_EMPTY_TABLES`
- Default: `false`

Whether the Target should create tables which have no records present in Remote.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set persist_empty_tables true

export TARGET_SNOWFLAKE_PERSIST_EMPTY_TABLES=true
```

### State Support

- Name: `state_support`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_STATE_SUPPORT`
- Default: `true`

Whether the Target should emit `STATE` messages to stdout for further consumption. In this mode, which is on by default, STATE messages are buffered in memory until all the records that occurred before them are flushed according to the batch flushing schedule the target is configured with.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set state_support false

export TARGET_SNOWFLAKE_STATE_SUPPORT=false
```

### Target S3: Bucket

- Name: `target_s3.bucket`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_TARGET_S3_BUCKET`

When included, use S3 to stage files.

Bucket where staging files should be uploaded to.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set target_s3 bucket <bucket>

export TARGET_SNOWFLAKE_TARGET_S3_BUCKET=<bucket>
```

### Target S3: Key Prefix

- Name: `target_s3.key_prefix`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_TARGET_S3_KEY_PREFIX`

Prefix for staging file uploads to allow for better delineation of tmp files.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set target_s3 key_prefix <prefix>

export TARGET_SNOWFLAKE_TARGET_S3_KEY_PREFIX=<prefix>
```

### Target S3: AWS Access Key ID

- Name: `target_s3.aws_access_key_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_TARGET_S3_AWS_ACCESS_KEY_ID`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set target_s3 aws_access_key_id <key_id>

export TARGET_SNOWFLAKE_TARGET_S3_AWS_ACCESS_KEY_ID=<key_id>
```

### Target S3: AWS Secret Access Key

- Name: `target_s3.aws_secret_access_key`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_TARGET_S3_AWS_SECRET_ACCESS_KEY`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set target_s3 aws_secret_access_key <key>

export TARGET_SNOWFLAKE_TARGET_S3_AWS_SECRET_ACCESS_KEY=<key>
```
