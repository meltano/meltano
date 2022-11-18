---
title: State Backends
description: State backends are used for persisting state between pipeline runs.
layout: doc
weight: 3
---

Many Meltano pipelines load data incrementally.
In order for these pipelines to run efficiently and properly without dropping historical data or loading duplicate records, Meltano needs to keep track of the state of a pipeline as part of each run.
This state can be stored in Meltano's backend system database, but
for Meltano projects running in ephemeral environments or in circumstances where administering a dedicated backend database is undesirable, Meltano also supports persisting state in remote state backends backed by cloud storage services.

## Installation

To cut down on extraneous dependencies, Meltano imports cloud storage client libraries lazily and these libraries are not included in the base `meltano` package.

Only the default system database state backend _or_ the local filesystem state backend can be used as part of the base `meltano` distribution.

To use a cloud storage backend, install Meltano using one of the following [extras](https://peps.python.org/pep-0508/#extras):

- `meltano[s3]` to use the AWS S3 state backend.
- `meltano[azure]` to use the Azure Blob Storage state backend.
- `meltano[gcs]` to use the Google Cloud Storage state backend.

## Currently Supported Backends

Depending on the environment where you're running Meltano and the state backend you wish to use, you may also need to configure additional settings. The settings for each currently supported backend are listed below and can also be found in [the Meltano settings reference documentation](/reference/settings#state-backends).

### System DB

By default, Meltano uses its backend system database.
If you've configured your project to use an alternative state backend and wish to use the default system database backend instead, just set the `state_backend.uri` setting to the special keyword value `systemdb`.

### Local Filesystem

To store state on the local filesystem, set the `state_backend.uri` setting to `file://<absolute path to the directory where you wish to store state>`.
The local filesystem state backend will utilize the lock settings described above.

### Azure Blob Storage

To store state remotely in Azure Blob Storage, set the `state_backend.uri` setting to `azure://<your container_name>/<prefix for state JSON blobs>`.

To authenticate to Azure, Meltano will also need a [connection string](https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string). You can provide this via the `state_backend.azure.connection_string` setting.
If no `state_backend.azure.connection_string` setting is configured, Meltano will use the value of the `AZURE_STORAGE_CONNECTION_STRING` environment variable.
If the connection string is not provided via either of these methods, Meltano will not be able to authenticate to Azure and any state operations will fail.

### AWS S3

To store state remotely in S3, set the `state_backend.uri` setting to `s3://<your bucket name>/<prefix for state JSON blobs>`.

To authenticate to AWS, you can provide an (AWS access key ID and AWS secret access key)[https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys] via either of the following methods:

- Configure the `state_backend.s3.aws_access_key_id` and `state_backend.s3.aws_secret_access_key` settings.
- Pass the access key ID and secret access key directly in the `state_backend.uri` by setting it to `s3://<aws_access_key_id>:<aws_secret_access_key>@<your bucket name>/<prefix for state JSON blobs>`.

If credentials are not provided via either of these methods, Meltano will use the values set in the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.
If these environment variables are not set, it will use the credentials stored in the environment's (AWS credentials file)[https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html].

If AWS credentials are not found via any of the methods described above, Meltano will not be able to authenticate to S3 and state operations will fail.

### Google Cloud Storage

To store state remotely in Google Cloud Storage, set the `state_backend.uri` setting to `gs://<your bucket name>/<prefix for state JSON blobs>`.

To authenticate to GCS, you must provide a path to a (service account credentials file)[https://cloud.google.com/iam/docs/creating-managing-service-account-keys]
These can be configured via the `state_backend.gcs.application_credentials` setting.

If credentials are not provided via these settings, Meltano will use the value the `GOOGLE_APPLICATION_CREDENTIALS` environment variable, if it is set.

If GCS credentials are not found via any of the methods described above, Meltano will not be able to authenticate to Google Cloud Storage and state operations will fail.

## Configuration

The state backend settings for your Meltano project can be configured much the same as any other Meltano setting. For some state backends, the only required setting is `state_backend.uri`.
By default, `state_backend.uri` is set to the special keyword string `systemdb`, which will tell Meltano to store state in the same backend database as it stores other project data.

It can be changed by running `meltano config meltano set state_backend.uri <URI for desired state backend>` or by directly editing a project's `meltano.yml` to add the following:

```yaml
state_backend:
    uri: <URI for desired state backend>
```

For some state backends and in some environments, `uri` is the only setting that needs to be configured in order to use a state backend other than the default `systemdb` backend. For instance, to store state directly on the local filesystem at the path `${MELTANO_SYS_DIR_ROOT}/state`, simply run `meltano config meltano set 'state_backend.uri file:///${MELTANO_SYS_DIR_ROOT}/state'`. Note the single quotes which prevent the early expansion of the environment variable.
Then Meltano will store the state for a given `state_id` at the path `file:///${MELTANO_SYS_DIR_ROOT}/state/<state_id>/state.json`.

### Locking

Because the `systemdb` state backend utilizes a transactional database, it can rely on the database's transaction logic to prevent conflicts among multiple runs of the same pipeline.
For some other state backends, Meltano implements its own simple locking mechanism.
This locking mechanism utilizes reasonable defaults but you may wish to configure the locking settings differently.
You can do this via two additional top-level `state_backend` settings: `state_backend.lock_timeout_seconds` and `state_backend.lock_retry_seconds`.

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

For example if you've been storing state in Meltano's system database and would like to migrate to S3, you'll need to first store state in a local json file, configure the S3 state backend, and then set state for your job using the local json file.

So to migrate state for a job with the state ID `dev:tap-github-to-target-jsonl`, you first need to ensure that your meltano project is configured to use the source state backend that currently holds the job state. For this example, we'll use `systemdb` as our source. To check the current configuration, run `meltano config meltano list` and then find the value for `state_backend.uri`:

```shell

$ meltano config meltano list | grep state_backend.uri

state_backend.uri [env: MELTANO_STATE_BACKEND_URI] current value: 'systemdb' (default)
```

Now that we've confirmed that our project is configured to use the correct source state backend, we can get the state for our job and write it to a local file:

```shell
$ meltano state get dev:tap-github-to-target-jsonl > dev:tap-github-to-target-jsonl.json
```

Now we need to reconfigure our meltano project to use the new destination state backend. For this example, we'll use an S3 bucket with the name `meltano` and store state under the prefix `state`.

```shell

$ meltano config meltano set state_backend.uri "s3://meltano/state"
Meltano setting 'state_backend.uri' was set in `.env`: 's3://meltano/state'

$ meltano config meltano set state_backend.s3.aws_access_key_id <AWS_ACCESS_KEY_ID>
Meltano setting 'state_backend.s3.aws_access_key_id' was set in `.env`: '(redacted)'

$ meltano config meltano set state_backend.s3.aws_secret_access_key <AWS_SECRET_ACCESS_KEY>
Meltano setting 'state_backend.s3.aws_secret_access_key' was set in `.env`: '(redacted)'
```

Now we can set the state in the new backend using the state file we just wrote:

```shell
$ meltano state set dev:tap-github-to-target-jsonl --input-file dev:tap-github-to-taget-jsonl.json
```

Meltano will prompt you to confirm:

```shell
This will overwrite the state's current value. Continue? [y/N]:
```

Enter `y` and then Meltano will write the job state to S3.

To do this quickly for multiple jobs, you can loop through the output of [`meltano state list`](command-line-interface#state) and use the `--force` flag for `meltano state set` to prevent confirmation prompts:

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
