---
title: State Backends
description: State backends are used for persisting state between pipeline runs.
layout: doc
sidebar_position: 3
---

Meltano is capable of running pipelines that load data incrementally.
In order for these pipelines to run efficiently and properly without losing historical data or loading duplicate records, Meltano needs to keep track of the state of a pipeline as part of each run.
This state can be stored in Meltano's backend system database, but
for Meltano projects running in ephemeral environments or in circumstances where administering a dedicated backend database is undesirable, Meltano also supports persisting state in remote state backends backed by cloud storage services.

## Supported Backends

- [System Database](#default-system-database)
- [Local Filesystem](#local-file-system)
- [Amazon AWS S3](#aws-s3)
- [Azure Blob Storage](#azure-blob-storage)
- [Google Cloud Storage](#google-cloud-storage)
- [Snowflake (External)](#snowflake-external)

### Beyond Basic Storage

With Meltano's flexible state backend architecture, you can store state in virtually any system that can store key-value data. Popular options include:

- **Cloud Data Warehouses**: Snowflake, BigQuery, Redshift, Databricks
- **Database Systems**: PostgreSQL, MySQL, MongoDB, Redis
- **Custom Solutions**: Your own API endpoints or enterprise storage systems

See our [Custom State Backends guide](/guide/custom-state-backend) to learn how to implement any of these options.

## Installation

No extra work is needed to use the default system database or local filesystem as a state backend as they are already part of any base Meltano distribution.

To use a cloud storage backend, install Meltano using one of the following [extras](https://peps.python.org/pep-0508/#extras):

- `meltano[s3]` to use the AWS S3 state backend.
- `meltano[azure]` to use the Azure Blob Storage state backend.
- `meltano[gcs]` to use the Google Cloud Storage state backend.

If the base Meltano distribution is already installed in your environment, install the relevant extra and `pip` will install only the missing requirements.

:::info
<p>
State backends are only available in Meltano version 2.10+. If you are using an earlier version, you'll need to upgrade your project via <a href="/reference/command-line-interface#upgrade"> <code>meltano upgrade</code></a> before you using the state backends feature.
</p>
:::

## Configuration

### Default (System Database)

The state backend settings for your Meltano project can be configured much the same as any other Meltano [setting](/reference/settings).
The main setting is `state_backend.uri` which is set to the special keyword string `systemdb` by default.
This will tell Meltano to store state in the same backend database as it stores other project data.

It can be changed by running `meltano config set meltano state_backend.uri <URI for desired state backend>` or by directly editing a project's `meltano.yml` to add the following:

```yaml
state_backend:
    uri: <URI for desired state backend>
```

### Local File System

To store state on the local filesystem, set the `state_backend.uri` setting to `file://<absolute path to the directory where you wish to store state>`.

For example, to store state directly on the local filesystem at the path `${MELTANO_SYS_DIR_ROOT}/state`, run:

```bash
meltano config set meltano state_backend.uri 'file:///${MELTANO_SYS_DIR_ROOT}/state'
```

Note the single quotes which prevent the early expansion of the environment variable.

Meltano will now store the state for a given `state_id` at the path `file:///${MELTANO_SYS_DIR_ROOT}/state/<state_id>/state.json`.

The local filesystem state backend will utilize the [locking strategy](#locking) described below.

### Azure Blob Storage

To store state remotely in Azure Blob Storage, set the `state_backend.uri` setting to `azure://<your container_name>/<prefix for state JSON blobs>`.

To authenticate to Azure, there are two possible approaches

- authorizing using [`DefaultAzureCredential`](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python), which can make use of a Managed Identity, CLI etc.
- authorizing with a Storage Account connection string

Meltano will try the `DefaultAzureCredential` approach first, before falling back to the connection string approach.

#### Using `DefaultAzureCredential`

To use the `DefaultAzureCredential` approach, you will need to provide the storage account URL in the [`state_backend.azure.storage_account_url`](/reference/settings/#state_backendazurestorage_account_url) setting.

The order in which the `DefaultAzureCredential` attempts to resolve authentication is described [in the Azure SDK documentation](https://learn.microsoft.com/en-gb/dotnet/azure/sdk/authentication/credential-chains?tabs=dac#defaultazurecredential-overview).
If you intend to use a `ManagedIdentity` for an Azure Host or similar, then you will also need to provide your identity client ID under the `AZURE_CLIENT_ID` environment variable.

An example environment variable configuration is given below:

```shell
MELTANO_STATE_BACKEND_URI='azure://meltano-state'
MELTANO_STATE_BACKEND_AZURE_STORAGE_ACCOUNT_URL='https://mystorageaccount.blob.core.windows.net/'
# only necessary if using ManagedIdentity
AZURE_CLIENT_ID='28a00fb0-67ee-4d11-81f8-10157e07c84f'
```

A benefit of this approach is that you do not need to enable shared key access to your Blob Storage Account.

#### Using an Azure connection string

You can provide a [connection string](https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string) to Meltano via the [`state_backend.azure.connection_string`](/reference/settings/#state_backendazureconnection_string) setting.
If no `state_backend.azure.connection_string` setting is configured, Meltano will use the value of the `AZURE_STORAGE_CONNECTION_STRING` environment variable.
If the connection string is not provided via either of these methods, Meltano will not be able to authenticate to Azure and any state operations will fail.

An example environment variable configuration is given below:

```shell
MELTANO_STATE_BACKEND_URI='azure://meltano-state'
AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=gSAw....'
```

### AWS S3

To store state remotely in S3, set the `state_backend.uri` setting to `s3://<your bucket name>/<prefix for state JSON blobs>`.

To authenticate to AWS, you can provide an [AWS access key ID and AWS secret access key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) via either of the following methods:

- Configure the `state_backend.s3.aws_access_key_id` and `state_backend.s3.aws_secret_access_key` settings.
- Pass the access key ID and secret access key directly in the `state_backend.uri` by setting it to `s3://<aws_access_key_id>:<aws_secret_access_key>@<your bucket name>/<prefix for state JSON blobs>`.

If credentials are not provided via either of these methods, Meltano will use the values set in the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.
If these environment variables are not set, it will use the credentials stored in the environment's [AWS credentials file](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

If AWS credentials are not found via any of the methods described above, Meltano will not be able to authenticate to S3 and state operations will fail.

#### Endpoint URL

Meltano supports service-specific endpoint URLs via:

* The `endpoint_url` setting in the shared AWS config file.
* The `AWS_ENDPOINT_URL` environment variable.
* The `AWS_ENDPOINT_URL_S3` environment variable.
* The Meltano [`state_backend.s3.endpoint_url`](/reference/settings#state_backends3endpoint_url) setting.

:::info
The `AWS_IGNORE_CONFIGURED_ENDPOINT_URLS` environment variable won't have any effect if `state_backend.s3.endpoint_url` is not null.
:::

For reference, read the [AWS documentation on service-specific endpoints](https://docs.aws.amazon.com/sdkref/latest/guide/feature-ss-endpoints.html).

### Google Cloud Storage

To store state remotely in Google Cloud Storage, set the `state_backend.uri` setting to `gs://<your bucket name>/<prefix for state JSON blobs>`.

To authenticate to GCS, you can provide service account credentials in one of the following ways:

#### Using a JSON credentials string

You can provide service account credentials directly as a JSON string via the [`state_backend.gcs.application_credentials_json`](/reference/settings/#state_backendgcsapplication_credentials_json) setting. This is the most production-friendly approach, especially in containerized environments.

```yaml
state_backend:
  uri: gs://my-bucket/state
  gcs:
    application_credentials_json: |
      {
        "type": "service_account",
        "project_id": "my-project",
        "private_key_id": "...",
        "private_key": "...",
        "client_email": "...",
        "client_id": "...",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "..."
      }
```

#### Using a credentials file path

You can provide a path to a [service account credentials file](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) via the [`state_backend.gcs.application_credentials_path`](/reference/settings/#state_backendgcsapplication_credentials_path) setting.

```yaml
state_backend:
  uri: gs://my-bucket/state
  gcs:
    application_credentials_path: /path/to/service-account-key.json
```

:::warning

The legacy `state_backend.gcs.application_credentials` setting is still supported but deprecated. Use `state_backend.gcs.application_credentials_path` instead.

:::

#### Default authentication

If credentials are not provided via any of the above settings, Meltano will use the value of the `GOOGLE_APPLICATION_CREDENTIALS` environment variable, if it is set.

### Snowflake (External)

Snowflake state backend support is available as a separate package: [`meltano-state-backend-snowflake`](https://github.com/meltano/meltano-state-backend-snowflake).

#### Installation

Install Meltano with the Snowflake state backend extension using one of these methods:

**Using uv:**
```bash
uv tool install --with meltano-state-backend-snowflake meltano
```

**Using pipx:**
```bash
pipx install meltano
pipx inject meltano 'meltano-state-backend-snowflake'
```

#### Configuration

To store state in Snowflake, set the `state_backend.uri` setting to `snowflake://<user>:<password>@<account>/<database>/<schema>`.

State will be stored in two tables that the extension will create automatically:
- `meltano_state` - Stores the actual state data
- `meltano_state_locks` - Manages concurrency locks

Example configuration using environment variables:

```bash
export MELTANO_STATE_BACKEND_URI='snowflake://my_user:my_password@my_account/my_database/my_schema'
```

#### Features

- Automatic table creation and management
- Concurrency control using database-level locking
- Support for JSON state data using Snowflake's VARIANT data type
- Flexible connection configuration with support for account, user, password, warehouse, database, schema, and role parameters
- Security best practices with environment variable configuration

For detailed configuration options and advanced features, see the [meltano-state-backend-snowflake documentation](https://github.com/meltano/meltano-state-backend-snowflake).

## Locking

Because the `systemdb` state backend utilizes a transactional database, it can rely on the database's transaction logic to prevent conflicts among multiple runs of the same pipeline.

For some other state backends, Meltano implements its own simple locking mechanism.
This locking mechanism utilizes reasonable defaults but you may wish to configure the locking settings differently.
You can do this via two [`state_backend` settings](/reference/settings#state-backends):

- `state_backend.lock_timeout_seconds`
- `state_backend.lock_retry_seconds`

When Meltano tries to read or write state for a given `state_id`, it will try to acquire a lock on the state data for that `state_id`.
For example, using the local filesystem state backend with `state_backend.uri` set to `file:///${MELTANO_SYS_DIR_ROOT}/state`, it will check to see if a file exists at the path `file:///${MELTANO_SYS_DIR_ROOT}/state/<state_id>/lock`.
If no such file exists, Meltano will create it and write the current UTC timestamp into the file.
If the file _does_ exist, Meltano will check the UTC timestamp written in the file to determine when it was locked by another process.
Meltano will add the configured value for `state_backend.lock_timeout_seconds` to the timestamp in the file to determine when the lock expires.
If the lock is expired (i.e. if the expiration time is _before_ the time at which Meltano attempts to acquire the new lock), then Meltano will overwrite the lock file with the current timestamp.
If the lock is _not_ expired, then Meltano will wait the number of seconds configured by the `state_backend.lock_retry_seconds` setting and then attempt to acquire the lock again.

In most deployments, it should be rare for the same pipeline to be running in parallel or for manual invocations of the `meltano state` command to take place during a pipeline's run. But if the default values for `lock_timeout_seconds` and `lock_retry_seconds` (10 seconds and 1 second, respectively) cause issues in your deployment, you can configure them to more appropriate values by running `meltano config meltano state_backend.lock_timeout_seconds <new value>` and `meltano config meltano state_backend.lock_retry_seconds <new value>` .

## Migrating State

You can migrate state from one backend to another backend using the [`meltano state get` and `meltano state set` commands](/reference/command-line-interface#state).

For example if you've been storing state in Meltano's system database and would like to migrate to S3, you'll need to first store state in a local JSON file, configure the S3 state backend, and then set state for your job using the local JSON file.

So to migrate state for a job with the state ID `dev:tap-github-to-target-jsonl`, you first need to ensure that your meltano project is configured to use the source state backend that currently holds the job state. For this example, we'll use `systemdb` as our source. To check the current configuration, run `meltano config list meltano` and then find the value for `state_backend.uri`:

```shell
$ meltano config list meltano | grep state_backend.uri

state_backend.uri [env: MELTANO_STATE_BACKEND_URI] current value: 'systemdb' (default)
```

Now that we've confirmed that our project is configured to use the correct source state backend, we can get the state for our job and write it to a local file:

```shell
$ meltano state get dev:tap-github-to-target-jsonl > dev:tap-github-to-target-jsonl.json
```

Now we need to reconfigure our meltano project to use the new destination state backend. For this example, we'll use an S3 bucket with the name `meltano` and store state under the prefix `state`.

```shell
$ meltano config set meltano state_backend.uri "s3://meltano/state"
Meltano setting 'state_backend.uri' was set in `.env`: 's3://meltano/state'

$ meltano config set meltano state_backend.s3.aws_access_key_id <AWS_ACCESS_KEY_ID>
Meltano setting 'state_backend.s3.aws_access_key_id' was set in `.env`: '(redacted)'

$ meltano config set meltano state_backend.s3.aws_secret_access_key <AWS_SECRET_ACCESS_KEY>
Meltano setting 'state_backend.s3.aws_secret_access_key' was set in `.env`: '(redacted)'
```

Now we can set the state in the new backend using the state file we just wrote:

```shell
$ meltano state set dev:tap-github-to-target-jsonl --input-file dev:tap-github-to-taget-jsonl.json
```

Meltano will prompt you to confirm:

```
This will overwrite the state's current value. Continue? [y/N]:
```

Enter `y` and then Meltano will write the job state to S3.

To do this quickly for multiple jobs, you can loop through the output of [`meltano state list`](/reference/command-line-interface#state) and use the `--force` flag for `meltano state set` to prevent confirmation prompts:

```shell
for job_id in $(meltano state list); do meltano state get $job_id > $job_id-state.json; done
```

To migrate state for some subset of state IDs, use the `--pattern` flag with `meltano state list`:

```shell
for job_id in $(meltano state list --pattern 'dev:*'); do meltano state get $job_id > $job_id-state.json; done
```

Then configure your project to use the S3 state backend as we did above.

Now loop through the state json files and set state in S3 for each one:

```shell
for state_file in *-state.json; do meltano state set --force ${state_file%-state.json} --input-file $state_file; done
```
