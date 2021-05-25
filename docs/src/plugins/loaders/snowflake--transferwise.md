---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into Snowflake
---

# Snowflake (`transferwise` variant)

The `target-snowflake` [loader](https://hub.meltano.com/loaders/) loads [extracted](https://hub.meltano.com/extractors/) data into a [Snowflake](https://www.snowflake.com/) data warehouse.

- **Repository**: <https://github.com/transferwise/pipelinewise-target-snowflake>
- **Documentation**: <https://transferwise.github.io/pipelinewise/connectors/targets/snowflake.html>
- **Maintainer**: [Wise](https://wise.com/)
- **Maintenance status**: Active

#### Alternative variants

Multiple [variants](/docs/plugins.html#variants) of `target-snowflake` are available.
This document describes the `transferwise` variant, which was originally built to be used with [PipelineWise](https://transferwise.github.io/pipelinewise/).

Alternative options are [`datamill-co`](./snowflake.html) (default) and [`meltano`](./snowflake--meltano.html).

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

Then, follow the steps in the ["Pre-requirements" section of the repository's README](https://github.com/transferwise/pipelinewise-target-snowflake/blob/master/README.md#pre-requirements).

### Installation and configuration

#### Using the Command Line Interface

1. Add the `transferwise` variant of the `target-snowflake` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-snowflake --variant transferwise
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the arrow next to the "Add to project" button for "Snowflake".
1. Choose "Add variant 'transferwise'".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`target-snowflake` requires the [configuration](/docs/configuration.html) of the following settings:

- [Account](#account)
- [DBname](#dbname)
- [User](#user)
- [Password](#password)
- [Warehouse](#warehouse)
- [S3 Bucket](#s3-bucket)
- [Stage](#stage)
- [File Format](#file-format)
- [Default Target Schema](#default-target-schema)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-snowflake` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-13}
plugins:
  loaders:
  - name: target-snowflake
    variant: transferwise
    config:
      account: rtxxxxx.eu-central-1
      dbname: MY_DATABASE
      user: my_user
      warehouse: MY_WAREHOUSE
      s3_bucket: my_bucket_name
      stage: "<SCHEMA>.<STAGE_OBJECT_NAME>"
      file_format: "<SCHEMA>.<FILE_FORMAT_OBJECT_NAME>"
      # default_target_schema: MY_SCHEMA    # override if default (see below) is not appropriate
```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_SNOWFLAKE_PASSWORD=my_password
```

### Account

- Name: `account`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_ACCOUNT`, alias: `SF_ACCOUNT`

Snowflake account name (i.e. `rtXXXXX.eu-central-1`)

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set account <account>

export TARGET_SNOWFLAKE_ACCOUNT=<account>
```

### DBname

- Name: `dbname`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DBNAME`, alias: `SF_DATABASE`

Snowflake Database name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set dbname <dbname>

export TARGET_SNOWFLAKE_DBNAME=<dbname>
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_USER`, alias: `SF_USER`

Snowflake User

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set user <user>

export TARGET_SNOWFLAKE_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PASSWORD`, alias: `SF_PASSWORD`

Snowflake Password

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set password <password>

export TARGET_SNOWFLAKE_PASSWORD=<password>
```

### Warehouse

- Name: `warehouse`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_WAREHOUSE`, alias: `SF_WAREHOUSE`

Snowflake virtual warehouse name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set warehouse <warehouse>

export TARGET_SNOWFLAKE_WAREHOUSE=<warehouse>
```

### S3 Bucket

- Name: `s3_bucket`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_S3_BUCKET`

S3 Bucket name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set s3_bucket <bucket_name>

export TARGET_SNOWFLAKE_S3_BUCKET=<bucket_name>
```

### Stage

- Name: `stage`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_STAGE`

Named external stage name created at pre-requirements section. Has to be a fully qualified name including the schema name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set stage <snowflake_external_stage_object_name>

export TARGET_SNOWFLAKE_STAGE=<snowflake_external_stage_object_name>
```

### File Format

- Name: `file_format`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_FILE_FORMAT`

Named file format name created at pre-requirements section. Has to be a fully qualified name including the schema name.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set file_format <snowflake_file_format_object_name>

export TARGET_SNOWFLAKE_FILE_FORMAT=<snowflake_file_format_object_name>
```

### Default Target Schema

- Name: `default_target_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA`, alias: `TARGET_SNOWFLAKE_SCHEMA`, `SF_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](https://hub.meltano.com/extractors/gitlab.html). Values are automatically converted to uppercase before they're passed on to the plugin, so `tap_gitlab` becomes `TAP_GITLAB`.

Name of the schema where the tables will be created, without database prefix. If `schema_mapping` is not defined then every stream sent by the tap is loaded into this schema.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set default_target_schema <schema>

export TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA=<schema>
```

### AWS Access Key ID

- Name: `aws_access_key_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_AWS_ACCESS_KEY_ID`

S3 Access Key Id. If not provided, `AWS_ACCESS_KEY_ID` environment variable or IAM role will be used

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set aws_access_key_id <key_id>

export TARGET_SNOWFLAKE_AWS_ACCESS_KEY_ID=<key_id>
```

### AWS Secret Access Key

- Name: `aws_secret_access_key`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_AWS_SECRET_ACCESS_KEY`

S3 Secret Access Key. If not provided, `AWS_SECRET_ACCESS_KEY` environment variable or IAM role will be used

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set aws_secret_access_key <key>

export TARGET_SNOWFLAKE_AWS_SECRET_ACCESS_KEY=<key>
```

### AWS Session Token

- Name: `aws_session_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_AWS_SESSION_TOKEN`

AWS Session token. If not provided, `AWS_SESSION_TOKEN` environment variable will be used

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set aws_session_token <token>

export TARGET_SNOWFLAKE_AWS_SESSION_TOKEN=<key>
```

### AWS Profile

- Name: `aws_profile`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_AWS_PROFILE`

AWS profile name for profile based authentication. If not provided, `AWS_PROFILE` environment variable will be used.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set aws_profile <token>

export TARGET_SNOWFLAKE_AWS_PROFILE=<key>
```

### S3 Key Prefix

- Name: `s3_key_prefix`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_S3_KEY_PREFIX`

A static prefix before the generated S3 key names. Using prefixes you can upload files into specific directories in the S3 bucket.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set s3_key_prefix <prefix>

export TARGET_SNOWFLAKE_S3_KEY_PREFIX=<prefix>
```

### S3 Endpoint URL

- Name: `s3_endpoint_url`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_S3_ENDPOINT_URL`

The complete URL to use for the constructed client. This is allowing to use non-native s3 account.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set s3_endpoint_url <url>

export TARGET_SNOWFLAKE_S3_ENDPOINT_URL=<url>
```

### S3 Region Name

- Name: `s3_region_name`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_S3_REGION_NAME`

Default region when creating new connections

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set s3_region_name <region>

export TARGET_SNOWFLAKE_S3_REGION_NAME=<region>
```

### S3 ACL

- Name: `s3_acl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_S3_ACL`

S3 ACL name to set on the uploaded files

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set s3_acl <acl>

export TARGET_SNOWFLAKE_S3_ACL=<acl>
```

### Batch Size Rows

- Name: `batch_size_rows`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_BATCH_SIZE_ROWS`
- Default: `100000`

Maximum number of rows in each batch. At the end of each batch, the rows in the batch are loaded into Snowflake.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set batch_size_rows 1000

export TARGET_SNOWFLAKE_BATCH_SIZE_ROWS=1000
```

### Flush All Streams

- Name: `flush_all_streams`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_FLUSH_ALL_STREAMS`
- Default: `false`

Flush and load every stream into Snowflake when one batch is full. Warning: This may trigger the COPY command to use files with low number of records, and may cause performance problems.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set flush_all_streams true

export TARGET_SNOWFLAKE_FLUSH_ALL_STREAMS=true
```

### Parallelism

- Name: `parallelism`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PARALLELISM`
- Default: `0`

The number of threads used to flush tables. 0 will create a thread for each stream, up to parallelism_max. -1 will create a thread for each CPU core. Any other positive number will create that number of threads, up to parallelism_max.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set parallelism -1

export TARGET_SNOWFLAKE_PARALLELISM=-1
```

### Parallelism Max

- Name: `parallelism_max`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PARALLELISM_MAX`
- Default: `16`

Max number of parallel threads to use when flushing tables.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set parallelism_max 8

export TARGET_SNOWFLAKE_PARALLELISM_MAX=8
```

### Default Target Schema Select Permission

- Name: `default_target_schema_select_permission`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA_SELECT_PERMISSION`

Grant USAGE privilege on newly created schemas and grant SELECT privilege on newly created tables to a specific role or a list of roles. If `schema_mapping` is not defined then every stream sent by the tap is granted accordingly.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set default_target_schema_select_permission <roles>

export TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA_SELECT_PERMISSION=<roles>
```

### Schema Mapping

- Name: `schema_mapping`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_SCHEMA_MAPPING`

Useful if you want to load multiple streams from one tap to multiple Snowflake schemas.

If the tap sends the `stream_id` in `<schema_name>-<table_name>` format then this option overwrites the `default_target_schema` value.

Note, that using `schema_mapping` you can overwrite the `default_target_schema_select_permission` value to grant SELECT permissions to different groups per schemas or optionally you can create indices automatically for the replicated tables.

This setting can hold an object mapping source schema names to objects with `target_schema` and (optionally) `target_schema_select_permissions` keys.

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{5-15}
plugins:
  loaders:
  - name: target-snowflake
    variant: transferwise
    config:
      schema_mapping:
        <source_schema>:
          target_schema: <target_schema>
          target_schema_select_permissions: [<role1>, <role2>] # Optional
        # ...

        # For example:
        public:
          target_schema: repl_sf_public
          target_schema_select_permissions: [grp_stats]
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set schema_mapping <source_schema> target_schema <target_schema>
meltano config target-snowflake set schema_mapping <source_schema> target_schema_select_permissions '["<role>", ...]'

export TARGET_SNOWFLAKE_SCHEMA_MAPPING='{"<source_schema>": {"target_schema": "<target_schema>", ...}, ...}'

# Once a schema mapping has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export TARGET_SNOWFLAKE_SCHEMA_MAPPING_<SOURCE_SCHEMA>_TARGET_SCHEMA=<target_schema>
export TARGET_SNOWFLAKE_SCHEMA_MAPPING_<SOURCE_SCHEMA>_TARGET_SCHEMA_SELECT_PERMISSIONS='["<role>", ...]'

# For example:
meltano config target-snowflake set schema_mapping public target_schema repl_sf_public
meltano config target-snowflake set schema_mapping public target_schema_select_permissions '["grp_stats"]'

export TARGET_SNOWFLAKE_SCHEMA_MAPPING_PUBLIC_TARGET_SCHEMA=new_repl_sf_public
```

### Disable Table Cache

- Name: `disable_table_cache`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DISABLE_TABLE_CACHE`
- Default: `false`

By default the connector caches the available table structures in Snowflake at startup. In this way it doesn't need to run additional queries when ingesting data to check if altering the target tables is required. With `disable_table_cache` option you can turn off this caching. You will always see the most recent table structures but will cause an extra query runtime.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set disable_table_cache true

export TARGET_SNOWFLAKE_DISABLE_TABLE_CACHE=true
```

### Client-Side Encryption Master Key

- Name: `client_side_encryption_master_key`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_CLIENT_SIDE_ENCRYPTION_MASTER_KEY`

When this is defined, Client-Side Encryption is enabled. The data in S3 will be encrypted, No third parties, including Amazon AWS and any ISPs, can see data in the clear. Snowflake COPY command will decrypt the data once it's in Snowflake. The master key must be 256-bit length and must be encoded as base64 string.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set client_side_encryption_master_key <key>

export TARGET_SNOWFLAKE_CLIENT_SIDE_ENCRYPTION_MASTER_KEY=<key>
```

### Client-Side Encryption Stage Object

- Name: `client_side_encryption_stage_object`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_CLIENT_SIDE_ENCRYPTION_STAGE_OBJECT`

Required when `client_side_encryption_master_key` is defined. The name of the encrypted stage object in Snowflake that created separately and using the same encryption master key.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set client_side_encryption_stage_object <stage_object>

export TARGET_SNOWFLAKE_CLIENT_SIDE_ENCRYPTION_STAGE_OBJECT=<stage_object>
```

### Add Metadata Columns

- Name: `add_metadata_columns`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_ADD_METADATA_COLUMNS`
- Default: `false`

Metadata columns add extra row level information about data ingestions, (i.e. when was the row read in source, when was inserted or deleted in snowflake etc.) Metadata columns are creating automatically by adding extra columns to the tables with a column prefix `_SDC_`. The column names are following the stitch naming conventions documented at <https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns>. Enabling metadata columns will flag the deleted rows by setting the `_SDC_DELETED_AT` metadata column. Without the `add_metadata_columns` option the deleted rows from singer taps will not be recongisable in Snowflake.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set add_metadata_columns true

export TARGET_SNOWFLAKE_ADD_METADATA_COLUMNS=true
```

### Hard Delete

- Name: `hard_delete`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_HARD_DELETE`
- Default: `false`

When `hard_delete` option is true then DELETE SQL commands will be performed in Snowflake to delete rows in tables. It's achieved by continuously checking the `_SDC_DELETED_AT` metadata column sent by the singer tap. Due to deleting rows requires metadata columns, `hard_delete` option automatically enables the `add_metadata_columns` option as well.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set hard_delete true

export TARGET_SNOWFLAKE_HARD_DELETE=true
```

### Data Flattening Max Level

- Name: `data_flattening_max_level`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_DATA_FLATTENING_MAX_LEVEL`
- Default: `0`

Object type RECORD items from taps can be loaded into VARIANT columns as JSON (default) or we can flatten the schema by creating columns automatically. When value is 0 (default) then flattening functionality is turned off.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set data_flattening_max_level 2

export TARGET_SNOWFLAKE_DATA_FLATTENING_MAX_LEVEL=2
```

### Primary Key Required

- Name: `primary_key_required`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_PRIMARY_KEY_REQUIRED`
- Default: `true`

Log based and Incremental replications on tables with no Primary Key cause duplicates when merging UPDATE events. When set to true, stop loading data if no Primary Key is defined.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set primary_key_required false

export TARGET_SNOWFLAKE_PRIMARY_KEY_REQUIRED=false
```

### Validate Records

- Name: `validate_records`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_VALIDATE_RECORDS`
- Default: `false`

Validate every single record message to the corresponding JSON schema. This option is disabled by default and invalid RECORD messages will fail only at load time by Snowflake. Enabling this option will detect invalid records earlier but could cause performance degradation.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set validate_records true

export TARGET_SNOWFLAKE_VALIDATE_RECORDS=true
```

### Temp Dir

- Name: `temp_dir`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_TEMP_DIR`
- Default: platform-dependent

Directory of temporary CSV files with RECORD messages.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set temp_dir /tmp/dir

export TARGET_SNOWFLAKE_TEMP_DIR=/tmp/dir
```

### No Compression

- Name: `no_compression`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_NO_COMPRESSION`
- Default: `false`

Generate uncompressed CSV files when loading to Snowflake. Normally, by default GZIP compressed files are generated.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set no_compression true

export TARGET_SNOWFLAKE_NO_COMPRESSION=true
```

### Query Tag

- Name: `query_tag`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_SNOWFLAKE_QUERY_TAG`

Optional string to tag executed queries in Snowflake. Replaces tokens `schema` and `table` with the appropriate values. The tags are displayed in the output of the Snowflake `QUERY_HISTORY`, `QUERY_HISTORY_BY_*` functions.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set query_tag <tag>

export TARGET_SNOWFLAKE_QUERY_TAG=<tag>
```
