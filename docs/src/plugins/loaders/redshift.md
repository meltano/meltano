---
sidebar: auto
description: Use Meltano to pull data from various sources and load it into Amazon Redshift
---

# Redshift

The `target-redshift` [loader](/plugins/loaders/) loads [extracted](/plugins/extractors/) data into an [Amzaon Redshift](https://aws.amazon.com/de/redshift/) database.

To learn more about `target-redshift`, refer to the repository at <https://github.com/transferwise/pipelinewise-target-redshift> and the [Transferwise documentation](transferwise.github.io/pipelinewise/connectors/targets/redshift.html).

#### Alternative variants

This document describes the `transferwise` variant, which was originally built to be used with [PipelineWise](https://transferwise.github.io/pipelinewise/).

Alternative options are currently not discoverable within Meltano.

## Getting Started

### Prerequisites

If you haven't already, follow the initial steps of the [Getting Started guide](/docs/getting-started.html):

1. [Install Meltano](/docs/getting-started.html#install-meltano)
1. [Create your Meltano project](/docs/getting-started.html#create-your-meltano-project)
1. [Add an extractor to pull data from a source](/docs/getting-started.html#add-an-extractor-to-pull-data-from-a-source)

### Installation and configuration

#### Using the Command Line Interface

1. Add the `transferwise` variant of the `target-redshift` loader to your project using [`meltano add`](/docs/command-line-interface.html#add):

    ```bash
    meltano add loader target-redshift
    ```

1. Configure the [settings](#settings) below using [`meltano config`](/docs/command-line-interface.html#config).

#### Using Meltano UI

1. Start [Meltano UI](/docs/ui.html) using [`meltano ui`](/docs/command-line-interface.html#ui):

    ```bash
    meltano ui
    ```

1. Open the Loaders interface at <http://localhost:5000/loaders>.
1. Click the arrow next to the "Add to project" button for "Amazon Redshift".
1. Configure the [settings](#settings) below in the "Configuration" interface that opens automatically.

### Next steps

Follow the remaining step of the [Getting Started guide](/docs/getting-started.html):

1. [Run a data integration (EL) pipeline](/docs/getting-started.html#run-a-data-integration-el-pipeline)

If you run into any issues, [learn how to get help](/docs/getting-help.html).

## Settings

`target-redshift` requires the [configuration](/docs/configuration.html) of the following settings:

- [Host](#host)
- [Port](#port)
- [User](#user)
- [Password](#password)
- [DBname](#dbname)
- [Default Target Schema](#default-target-schema)
- [S3 Bucket](#s3_bucket)

These and other supported settings are documented below.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

#### Minimal configuration

A minimal configuration of `target-redshift` in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file) will look like this:

```yml{5-13}
plugins:
  loaders:
  - name: target-redshift
    variant: transferwise
    config:
      host: postgres.example.com
      port: 5432
      user: my_user
      dbname: my_database
      # default_target_schema: my_schema   # override if default (see below) is not appropriate
      s3_bucket: my-s3-bucket-name
      # AWS credential settings 
      aws_profile: my_aws_cli_profile
      # alternatively AWS IAM User key and secret
      aws_access_key_id: my_aws_access_key
      aws_secret_access_key: my_aws_access_secret
      # AWS role to be used by the COPY command to load datafrom S3 into Redshift
      aws_redshift_copy_role_arn: arn:aws:iam::<account_if>:role/<role name>

```

Sensitive values are most appropriately stored in [the environment](/docs/configuration.html#configuring-settings) or your project's [`.env` file](/docs/project.html#env):

```bash
export TARGET_REDSHIFT_PASSWORD=my_password
```

### Host

- Name: `host`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_HOST`
- Default: `localhost`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set host <host>

export TARGET_REDSHIFT_HOST=<host>
```

### Port

- Name: `port`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_PORT`
- Default: `5432`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set port 5502

export TARGET_REDSHIFT_PORT=5502
```

### User

- Name: `user`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_USER`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set user <user>

export TARGET_REDSHIFT_USER=<user>
```

### Password

- Name: `password`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_PASSWORD`

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set password <password>

export TARGET_REDSHIFT_PASSWORD=<password>
```

### DBname

- Name: `dbname`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_DBNAME`

PostgreSQL database name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set dbname <dbname>

export TARGET_REDSHIFT_DBNAME=<dbname>
```

### AWS Profile

- Name: `aws_profile`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_AWS_PROFILE`
- Default: 

AWS profile name for profile based authentication. If not provided, AWS_PROFILE environment variable will be used.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set aws_profile <aws profile name>

export TARGET_REDSHIFT_AWS_PROFILE=<aws profile name>
```

### AWS Access Key ID

- Name: `aws_access_key_id`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_AWS_ACCESS_KEY_ID`
- Default: 

AWS Access Key Id. Used for S3 and Redshfit copy operations. If not provided, AWS_ACCESS_KEY_ID environment variable will be used.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set aws_access_key_id <aws access key>

export TARGET_REDSHIFT_AWS_ACCESS_KEY_ID=<aws access key>
```

### AWS Secret Access Key

- Name: `aws_secret_access_key`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_AWS_SECRET_ACCESS_KEY`
- Default: 

AWS Secret Access Key. Used for S3 and Redshfit copy operations. If not provided, AWS_SECRET_ACCESS_KEY environment variable will be used.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set aws_secret_access_key <aws secret access key>

export TARGET_REDSHIFT_AWS_SECRET_ACCESS_KEY=<aws secret access key>
```

### AWS Session Token

- Name: `aws_session_token`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_AWS_SESSION_TOKEN`
- Default: 

AWS STS token for temporary credentials. If not provided, AWS_SESSION_TOKEN environment variable will be used.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set aws_session_token <aws sts session token>

export TARGET_REDSHIFT_AWS_SESSION_TOKEN=<aws sts session token>
```

### AWS Redshift Copy Role ARN

- Name: `aws_redshift_copy_role_arn`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_AWS_REDSHIFT_COPY_ROLE_ARN`
- Default: 

AWS Role ARN to be used for the Redshift COPY operation. Used instead of the given AWS keys for the COPY operation if provided - the keys are still used for other S3 operations.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set aws_redshift_copy_role_arn <aws role arn>

export TARGET_REDSHIFT_AWS_REDSHIFT_COPY_ROLE_ARN=<aws role arn>
```

### S3 ACL

- Name: `s3_acl`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_S3_ACL`
- Default: 

S3 Object ACL to be applied to files created in S3 bucket.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set s3_acl <s3 acl>

export TARGET_REDSHIFT_S3_ACL=<s3 acl>
```

### S3 Bucket

- Name: `s3_bucket`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_S3_BUCKET`
- Default: 

Unique S3 Bucket name

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set s3_bucket <s3 bucket>

export TARGET_REDSHIFT_S3_BUCKET=<s3 bucket>
```

### s3_key_prefix

- Name: `s3_key_prefix`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_S3_KEY_PREFIX`
- Default: 

A static prefix before the generated S3 key names. Using prefixes you can upload files into specific directories in the S3 bucket.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set s3_key_prefix <s3 keyprefix>

export TARGET_REDSHIFT_S3_KEY_PREFIX=<s3 key prefix>
```

### Copy Options

- Name: `copy_options`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_COPY_OPTIONS`
- Default: `EMPTYASNULL BLANKSASNULL TRIMBLANKS TRUNCATECOLUMNS TIMEFORMAT 'auto' COMPUPDATE OFF STATUPDATE OFF`

Parameters to use in the COPY command when loading data to Redshift. Some basic file formatting parameters are fixed values and not recommended overriding them by custom values. They are like: CSV GZIP DELIMITER ',' REMOVEQUOTES ESCAPE

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set copy_options <copy_options>

export TARGET_REDSHIFT_COPY_OPTIONS=<copy_options>
```

### Default Target Schema

- Name: `default_target_schema`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA`
- Default: `$MELTANO_EXTRACT__LOAD_SCHEMA`, which [will expand to](/docs/configuration.html#expansion-in-setting-values) the value of the [`load_schema` extra](/docs/plugins.html#load-schema-extra) for the extractor used in the pipeline, which defaults to the extractor's namespace, e.g. `tap_gitlab` for [`tap-gitlab`](/plugins/extractors/gitlab.html).

Name of the schema where the tables will be created. If `schema_mapping` is not defined then every stream sent by the tap is loaded into this schema.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set default_target_schema <schema>

export TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA=<schema>
```

### Batch Size Rows

- Name: `batch_size_rows`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_BATCH_SIZE_ROWS`
- Default: `100000`

Maximum number of rows in each batch. At the end of each batch, the rows in the batch are loaded into Postgres.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set batch_size_rows 1000

export TARGET_REDSHIFT_BATCH_SIZE_ROWS=1000
```

### Flush All Streams

- Name: `flush_all_streams`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_FLUSH_ALL_STREAMS`
- Default: `false`

Flush and load every stream into Postgres when one batch is full. Warning: This may trigger the COPY command to use files with low number of records.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set flush_all_streams true

export TARGET_REDSHIFT_FLUSH_ALL_STREAMS=true
```

### Parallelism

- Name: `parallelism`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_PARALLELISM`
- Default: `0`

The number of threads used to flush tables. 0 will create a thread for each stream, up to parallelism_max. -1 will create a thread for each CPU core. Any other positive number will create that number of threads, up to parallelism_max.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set parallelism -1

export TARGET_REDSHIFT_PARALLELISM=-1
```

### Max Parallelism

- Name: `max_parallelism`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_MAX_PARALLELISM`
- Default: `16`

Max number of parallel threads to use when flushing tables.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set max_parallelism 8

export TARGET_REDSHIFT_MAX_PARALLELISM=8
```

### Default Target Schema Select Permission

- Name: `default_target_schema_select_permission`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA_SELECT_PERMISSION`

Grant USAGE privilege on newly created schemas and grant SELECT privilege on newly created tables to a specific role or a list of roles. If `schema_mapping` is not defined then every stream sent by the tap is granted accordingly.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-snowflake set default_target_schema_select_permission <roles>

export TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA_SELECT_PERMISSION=<roles>
```

### Schema Mapping

- Name: `schema_mapping`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_SCHEMA_MAPPING`

Useful if you want to load multiple streams from one tap to multiple Postgres schemas.

If the tap sends the `stream_id` in `<schema_name>-<table_name>` format then this option overwrites the `default_target_schema` value.

Note, that using `schema_mapping` you can overwrite the `default_target_schema_select_permission` value to grant SELECT permissions to different groups per schemas or optionally you can create indices automatically for the replicated tables.

This setting can hold an object mapping source schema names to objects with `target_schema` and (optionally) `target_schema_select_permissions` keys.

#### How to use

Manage this setting directly in your [`meltano.yml` project file](/docs/project.html#meltano-yml-project-file):

```yml{5-15}
plugins:
  loaders:
  - name: target-redshift
    variant: transferwise
    config:
      schema_mapping:
        <source_schema>:
          target_schema: <target_schema>
          target_schema_select_permissions: [<role1>, <role2>] # Optional
        # ...

        # For example:
        public:
          target_schema: repl_pg_public
          target_schema_select_permissions: [grp_stats]
```

Alternatively, manage this setting using [`meltano config`](/docs/command-line-interface.html#config) or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set schema_mapping <source_schema> target_schema <target_schema>
meltano config target-redshift set schema_mapping <source_schema> target_schema_select_permissions '["<role>", ...]'

export TARGET_REDSHIFT_SCHEMA_MAPPING='{"<source_schema>": {"target_schema": "<target_schema>", ...}, ...}'

# Once a schema mapping has been set in `meltano.yml`, environment variables can be used
# to override specific nested properties:
export TARGET_REDSHIFT_SCHEMA_MAPPING_<SOURCE_SCHEMA>_TARGET_SCHEMA=<target_schema>
export TARGET_REDSHIFT_SCHEMA_MAPPING_<SOURCE_SCHEMA>_TARGET_SCHEMA_SELECT_PERMISSIONS='["<role>", ...]'

# For example:
meltano config target-redshift set schema_mapping public target_schema repl_pg_public
meltano config target-redshift set schema_mapping public target_schema_select_permissions '["grp_stats"]'

export TARGET_REDSHIFT_SCHEMA_MAPPING_PUBLIC_TARGET_SCHEMA=new_repl_pg_public
```

### Disable Table Cache

- Name: `disable_table_cache`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_DISABLE_TABLE_CACHE`
- Default: `false`

By default the connector caches the available table structures in Redshift at startup. In this way it doesn't need to run additional queries when ingesting data to check if altering the target tables is required. With disable_table_cache option you can turn off this caching. You will always see the most recent table structures but will cause an extra query runtime.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set disable_table_cache true

export TARGET_REDSHIFT_DISABLE_TABLE_CACHE=true
```

### Add Metadata Columns

- Name: `add_metadata_columns`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_ADD_METADATA_COLUMNS`
- Default: `false`

Metadata columns add extra row level information about data ingestions, (i.e. when was the row read in source, when was inserted or deleted in postgres etc.) Metadata columns are creating automatically by adding extra columns to the tables with a column prefix `_SDC_`. The column names are following the stitch naming conventions documented at <https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns>. Enabling metadata columns will flag the deleted rows by setting the `_SDC_DELETED_AT` metadata column. Without the `add_metadata_columns` option the deleted rows from singer taps will not be recongisable in Postgres.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set add_metadata_columns true

export TARGET_REDSHIFT_ADD_METADATA_COLUMNS=true
```

### Hard Delete

- Name: `hard_delete`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_HARD_DELETE`
- Default: `false`

When `hard_delete` option is true then DELETE SQL commands will be performed in Postgres to delete rows in tables. It's achieved by continuously checking the `_SDC_DELETED_AT` metadata column sent by the singer tap. Due to deleting rows requires metadata columns, `hard_delete` option automatically enables the `add_metadata_columns` option as well.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set hard_delete true

export TARGET_REDSHIFT_HARD_DELETE=true
```

### Data Flattening Max Level

- Name: `data_flattening_max_level`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_DATA_FLATTENING_MAX_LEVEL`
- Default: `0`

Object type RECORD items from taps can be transformed to flattened columns by creating columns automatically. When value is 0 (default) then flattening functionality is turned off.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set data_flattening_max_level 2

export TARGET_REDSHIFT_DATA_FLATTENING_MAX_LEVEL=2
```

### Primary Key Required

- Name: `primary_key_required`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_PRIMARY_KEY_REQUIRED`
- Default: `true`

Log based and Incremental replications on tables with no Primary Key cause duplicates when merging UPDATE events. When set to true, stop loading data if no Primary Key is defined.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set primary_key_required false

export TARGET_REDSHIFT_PRIMARY_KEY_REQUIRED=false
```

### Validate Records

- Name: `validate_records`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_VALIDATE_RECORDS`
- Default: `false`

Validate every single record message to the corresponding JSON schema. This option is disabled by default and invalid RECORD messages will fail only at load time by Postgres. Enabling this option will detect invalid records earlier but could cause performance degradation.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set validate_records true

export TARGET_REDSHIFT_VALIDATE_RECORDS=true
```

### Skip Updates

- Name: `skip_updates`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_SKIP_UPDATES`
- Default: `false`

Do not update existing records when Primary Key is defined. Useful to improve performance when records are immutable, e.g. events.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set skip_updates true

export TARGET_REDSHIFT_SKIP_UPDATES=true
```

### Compression 

- Name: `compression`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_COMPRESSION`
- Default: 

The compression method to use when writing files to S3 and running Redshift COPY. The currently supported methods are gzip or bzip2.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set compression gzip

export TARGET_REDSHIFT_COMPRESSION=gzip
```

### Slices

- Name: `slices`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_SLICES`
- Default: 1

The number of slices to split files into prior to running COPY on Redshift. This should be set to the number of Redshift slices. The number of slices per node depends on the node size of the cluster - run SELECT COUNT(DISTINCT slice) slices FROM stv_slices to calculate this.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set slices 2

export TARGET_REDSHIFT_SLICES=2
```

### Temp Dir

- Name: `temp_dir`
- [Environment variable](/docs/configuration.html#configuring-settings): `TARGET_REDSHIFT_TEMP_DIR`
- Default: platform-dependent

Directory of temporary CSV files with RECORD messages.

#### How to use

Manage this setting using [Meltano UI](#using-meltano-ui), [`meltano config`](/docs/command-line-interface.html#config), or an [environment variable](/docs/configuration.html#configuring-settings):

```bash
meltano config target-redshift set temp_dir /tmp/dir

export TARGET_REDSHIFT_TEMP_DIR=/tmp/dir
```


