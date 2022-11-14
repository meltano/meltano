---
title: Settings
description: Meltano supports a number of settings that allow you to fine tune its behavior, which are documented here.
layout: doc
weight: 2
---

Meltano supports a number of settings that allow you to fine tune its behavior, which are documented here.
To quickly find the setting you're looking for, use the Table of Contents in the sidebar.

As described in the [Configuration guide](/guide/configuration#configuration-layers), Meltano will determine the values of these settings by first looking in [**the environment**](/guide/configuration#configuring-settings), then in your project's [**`.env` file**](/concepts/project#env), and finally in your [**`meltano.yml` project file**](/concepts/project#meltano-yml-project-file), falling back to a default value if nothing was found.

You can use [`meltano config meltano list`](/reference/command-line-interface#config) to list all available settings with their names, [environment variables](/guide/configuration#configuring-settings), and current values.

Configuration that is _not_ environment-specific or sensitive should be stored in your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file) and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment or your project's [`.env` file](/concepts/project#env).

[`meltano config meltano set <setting> <value>`](/reference/command-line-interface#config), which is used in the examples below, will automatically store configuration in `meltano.yml` or `.env` as appropriate.

If supported by the plugin type, its configuration can be tested using [`meltano config <plugin> test`](/reference/command-line-interface#config).

## Plugin settings

For plugin settings, refer to the specific plugin's documentation
([extractors](https://hub.meltano.com/extractors/), [loaders](https://hub.meltano.com/loaders/)),
or use [`meltano config <plugin> list`](/reference/command-line-interface#config)
to list all available settings with their names, environment variables, and current values.

## Your Meltano project

These are settings specific to [your Meltano project](/concepts/project).

### <a name="send-anonymous-usage-stats"></a>`send_anonymous_usage_stats`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_SEND_ANONYMOUS_USAGE_STATS`
- [`meltano init`](/reference/command-line-interface#init) CLI option: `--no_usage_stats` (implies value `false`)
- Default: `true`

Meltano is open source software thats free for anyone to use. The best thing a user could do to give back to the community, aside from contributing code or reporting issues, is contribute anonymous usage stats to allow the maintainers to understand how features are being utilized ultimately helping the community build a better product.

By default, Meltano shares anonymous usage data with the Meltano team using Snowplow. We use this data to learn about the size of our user base and the specific Meltano features they are using, which helps us determine the highest impact changes we can make in each release to make Meltano even more useful for you and others like you.

We also provide some of this data back to the community via [MeltanoHub](https://hub.meltano.com/) to help users understand the overall usage of plugins within Meltano.

If enabled, Meltano will use the value of the [`project_id` setting](#project-id) to uniquely identify your project. If the project ID is a UUID, then it will be sent unchanged. Otherwise, it will be [hashed](#q-what-is-a-one-way-hash-and-how-is-it-helpful), and its hash will be used to derive a UUID which will be used to uniquely identify your project.

This project ID is also sent along when Meltano requests available plugins from the URLs identified by the [`hub_url`](#hub-url) or [`discovery_url` setting](#discovery-url).

If you'd like to send the tracking data to a different Snowplow account than the one run by the Meltano team,
the collector endpoints can be configured using the [`snowplow.collector_endpoints` setting](#snowplowcollector_endpoints).

See more about our [anonymization standards](#anonymization-standards) and [anonymous usage stats Q&A](#anonymous-usage-stats-qa) below for more details.
Also refer to the Meltano data team handbook page for our ["Philosophy of Telemetry"](https://handbook.meltano.com/data-team/telemetry#philosophy-of-telemetry).

With all that said, if you'd still prefer to use Meltano _without_ sending the maintainers this kind of data, you're able to disable tracking entirely using one of these methods:

- When creating a new project, pass `--no_usage_stats` to [`meltano init`](/reference/command-line-interface#init)
- In an existing project, set the `send_anonymous_usage_stats` setting to `false`
- To disable tracking in all projects in one go, set the `MELTANO_SEND_ANONYMOUS_USAGE_STATS` environment variable to `false`

#### How to use

```bash
meltano config meltano set send_anonymous_usage_stats false

export MELTANO_SEND_ANONYMOUS_USAGE_STATS=false

meltano init --no_usage_stats demo-project
```

#### Anonymization Standards

Unless otherwise approved, any user-entered data is anonymized client-side before being submitted to Meltano. This section describes which data is sent in clear text and which data is obfuscated via one-way hashing.

We capture these in clear text:

- plugin names
- plugin variant names
- command names
- execution context, such as:
  - OS version
  - Python version
  - project ID

We anonymize these with one-way hashing before reporting:

- CLI args
- plugin config

These items will never be collected or reported back to meltano:

- your settings values
- your secrets or credentials
- the contents of your `meltano.yml` file

#### Anonymous Usage Stats Q&A

##### Q: What is a one way hash and how is it helpful?

**A:**

One-way hashing is a way of obfuscating sensitive data such that:

1. The same input value always produces the same output value (aka "hash").
2. The results are mathematically and statistically _extremely difficult_ (read: near impossible) to reverse engineer back to the source value.
3. Hash results are extremely helpful in safely and anonymously detecting changes to a file or configuration. Without passing the entire configuration, and without providing a hacker any means of decoding/decrypting the data back to its source, we can see that a file (such as `meltano.yml`) has not changed since its last hash was generated.

##### Q: Why does Meltano use hashing?

**A:**

Meltano hashes any fields at all which could be used by a hacker to compromise a project or user. We will never know what freeform text arguments you passed in via the command line, we won't have any data at all which could be used to compromise your environment, and whatever data we collect, we'll never sell, share, or trade your data with any third parties.

##### Should I enable or disable anonymous reporting?

**A:**

We hope you will choose to enable reporting, because this really does help us - and it helps the Meltano community in a very real way.

If you still have any concerns about keeping anonymous reporting enabled, we hope you'll share those concerns with us. You can do so by emailing `hello@meltano.com` or by logging an issue in our [Meltano Issue Tracker](https://github.com/meltano/meltano/issues).

### <a name="project-id"></a>`project_id`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_PROJECT_ID`
- Default: None

Used by Meltano to uniquely identify your project if the [`send_anonymous_usage_stats` setting](#send-anonymous-usage-stats) is enabled.

#### How to use

```bash
meltano config meltano set project_id '<unique identifier>'

export MELTANO_PROJECT_ID='<unique identifier>'
```

### <a name="database-uri"></a>`database_uri`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_DATABASE_URI`
- `meltano *` CLI option: `--database-uri`
- Default: `sqlite:///$MELTANO_SYS_DIR_ROOT/meltano.db`

Meltano stores various types of metadata in a project-specific [system database](/concepts/project#system-database),
that takes the shape of a SQLite database stored inside the [`.meltano` directory](/concepts/project#meltano-directory) at `.meltano/meltano.db` by default.

You can choose to use a different system database backend or configuration using the `--database-uri`
option of [`meltano` subcommands](/reference/command-line-interface), or the `MELTANO_DATABASE_URI` environment variable.

#### How to use

```bash
meltano config meltano set database_uri postgresql://<username>:<password>@<host>:<port>/<database>

export MELTANO_DATABASE_URI=postgresql://<username>:<password>@<host>:<port>/<database>

meltano elt --database-uri=postgresql://<username>:<password>@<host>:<port>/<database> ...
```

#### Targeting a PostgreSQL Schema

When using PostgreSQL as your [system database](/concepts/project#system-database), you can choose the target schema within that database by adding
`?options=-csearch_path%3D<schema>` directly to the end of your `database_uri` and `MELTANO_DATABASE_URI`.

You are also able to add multiple schemas, which PostgreSQL will work through from left to right until it finds a valid schema to target, by using `?options=-csearch_path%3D<schema>,<schema_two>`

If you dont target a schema then by default PostgreSQL will try to use the `public` schema.

```bash
postgresql://<username>:<password>@<host>:<port>/<database>?options=-csearch_path%3D<schema>
```

### `database_max_retries`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_DATABASE_MAX_RETRIES`
- Default: `3`

This sets the maximum number of reconnection attempts in case the initial connection to the database fails because it isn't available when Meltano starts up.

Note: This affects the initial connection attempt only after which the connection is cached.
Subsequent disconnections are handled by SQLALchemy

#### How to use

```bash
meltano config meltano set database_max_retries 3

export MELTANO_DATABASE_MAX_RETRIES=3
```

### `database_retry_timeout`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_DATABASE_RETRY_TIMEOUT`
- Default: `5` (seconds)

This controls the retry interval (in seconds) in case the initial connection to the database fails because it isn't available when Meltano starts up.

Note: This affects the initial connection attempt only after which the connection is cached.
Subsequent disconnections are handled by SQLALchemy

#### How to use

```bash
meltano config meltano set database_retry_timeout 5

export MELTANO_DATABASE_RETRY_TIMEOUT=5
```

### <a name="project-readonly"></a>`project_readonly`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_PROJECT_READONLY`
- Default: `false`

Enable this setting to indicate that your Meltano project is deployed as read-only,
and to block all modifications to project files through the [CLI](/reference/command-line-interface) and [UI](/reference/command-line-interface#ui)
in this environment.

Specifically, this prevents [adding plugins](/reference/command-line-interface#add) or [pipeline schedules](/reference/command-line-interface#schedule) to your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file), as well as [modifying plugin configuration](/reference/command-line-interface#config) stored in [`meltano.yml`](/concepts/project#meltano-yml-project-file) or [`.env`](/concepts/project#env).

Note that [`meltano config <plugin> set`](/reference/command-line-interface#config)
can still be used to store configuration in the [system database](/concepts/project#system-database),
but that settings that are already [set in the environment](/guide/configuration#configuring-settings) or `meltano.yml` take precedence and cannot be overridden.

#### How to use

```bash
meltano config meltano set project_readonly true

export MELTANO_PROJECT_READONLY=true
```

### <a name="hub-api-root"></a>`hub_api_root`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_HUB_API_ROOT`
- Default: None

This sets the value of the root url for the hub api.

If provided, this setting overrides the [`hub_url`](#hub-url).

#### How to use

```bash
meltano config meltano set hub_api_root "https://mysite.com/my-plugins"
meltano config meltano set hub_api_root false

export MELTANO_HUB_API_ROOT="https://mysite.com/my-plugins"
export MELTANO_HUB_API_ROOT=false
```

### <a name="hub-url"></a>`hub_url`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_HUB_URL`
- Default: `https://hub.meltano.com`

Where Meltano can find the Hub that lists all [discoverable plugins](/concepts/plugins#discoverable-plugins).

This manifest is primarily used by [`meltano discover`](/reference/command-line-interface#discover) and [`meltano add`](/reference/command-line-interface#add). It is also used in cases where the full plugin definition is needed but no lock artifact or cached `discovery.yml` is found.

#### How to use

```bash
meltano config meltano set hub_url http://localhost:4000

export MELTANO_HUB_URL=http://localhost:4000
```

### <a name="hub-url-auth"></a>`hub_url_auth`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_HUB_URL_AUTH`
- Default: None

The value of the `Authorization` header sent when making a request to [`hub_url`](#hub-url).

No `Authorization` header is applied under the following conditions:

- `hub_url_auth` is not set
- `hub_url_auth` is set to `false`, `null` or an empty string

#### How to use

```bash
meltano config meltano set hub_url_auth "Bearer $ACCESS_TOKEN"
meltano config meltano set hub_url_auth false

export MELTANO_HUB_URL_AUTH="Bearer $ACCESS_TOKEN"
export MELTANO_HUB_URL_AUTH=false
```

### <a name="discovery-url"></a>`discovery_url`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_DISCOVERY_URL`
- Default: [`https://discovery.meltano.com/discovery.yml`](https://discovery.meltano.com/discovery.yml)

Where Meltano can find the `discovery.yml` manifest that lists all [discoverable plugins](/concepts/plugins#discoverable-plugins) that are supported out of the box.

This manifest is used by [`meltano discover`](/reference/command-line-interface#discover) and [`meltano add`](/reference/command-line-interface#add), among others.

To disable downloading the remote `discovery.yml` manifest and only use the project-local or packaged version,
set this setting to `false` or any other string not starting with `http://` or `https://`.

#### How to use

```bash
meltano config meltano set discovery_url https://meltano.example.com/discovery.yml
meltano config meltano set discovery_url false

export MELTANO_DISCOVERY_URL=https://meltano.example.com/discovery.yml
export MELTANO_DISCOVERY_URL=false
```

### `discovery_url_auth`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_DISCOVERY_URL_AUTH`
- Default: None

The value of the `Authorization` header sent when making a request to [`discovery_url`](#discovery-url).

No `Authorization` header is applied under the following conditions:

- `discovery_url_auth` is not set
- `discovery_url_auth` is set to `false`, `null` or an empty string

#### How to use

```bash
meltano config meltano set discovery_url_auth "Bearer $ACCESS_TOKEN"
meltano config meltano set discovery_url_auth false

export MELTANO_DISCOVERY_URL_AUTH="Bearer $ACCESS_TOKEN"
export MELTANO_DISCOVERY_URL_AUTH=false
```

## `meltano` CLI

These settings can be used to modify the behavior of the [`meltano` CLI](/reference/command-line-interface).

### <a name="cli-log-level"></a>`cli.log_level`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_CLI_LOG_LEVEL`, alias: `MELTANO_LOG_LEVEL`
- `meltano` CLI option: `--log-level`
- Options: `debug`, `info`, `warning`, `error`, `critical`
- Default: `info`

The granularity of CLI logging. Ignored if a local logging config is found.

#### How to use

```bash
meltano config meltano set cli log_level debug

export MELTANO_CLI_LOG_LEVEL=debug
export MELTANO_LOG_LEVEL=debug

meltano --log-level=debug ...
```

### `cli.log_config`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_CLI_LOG_CONFIG`, alias: `MELTANO_LOG_CONFIG`
- `meltano` CLI option: `--log-config`
- Default: `logging.yaml`

The path of a valid yaml formatted [python logging dict config file](https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema) to use to configure logging _if present_.

#### How to use

```bash
meltano config meltano set cli log_config /path/to/logging.yaml

export MELTANO_CLI_LOG_CONFIG=/path/to/logging.yaml
export MELTANO_LOG_CONFIG=/path/to/logging.yaml

meltano --log-config=/path/to/logging.yaml ...
```

A sample logging config:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: True
  key_value:
    (): meltano.core.logging.key_value_formatter
    sort_keys: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: structured_colored
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: /var/log/meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

## `meltano elt`

These settings can be used to modify the behavior of [`meltano elt`](/reference/command-line-interface#elt).

### `elt.buffer_size`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_ELT_BUFFER_SIZE`
- Default: `10485760` (10MiB in bytes)

Size (in bytes) of the buffer between extractor and loader (Singer tap and target) that stores
[messages](https://hub.meltano.com/singer/spec#messages)
output by the extractor while they are waiting to be processed by the loader.

When an extractor generates messages (records) faster than the loader can process them, the buffer may fill up completely,
at which point the extractor will be blocked until the loader has worked through enough messages to make half
of the buffer size available again for new extractor output.

The length of a single line of extractor output is limited to half the buffer size.
With a default buffer size of 10MiB, the maximum message size would therefore be 5MiB.

#### How to use

```bash
meltano config meltano set elt.buffer_size 52428800 # 50MiB in bytes

export MELTANO_ELT_BUFFER_SIZE=52428800
```
## State Backends

### <a name="state-backend-uri"></a>`state_backend.uri`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_BACKEND_URI`
- Default: `systemdb`

URI for the [state backend](/concepts/state_backends) where you'd like Meltano to store state.

#### How to use

```bash
meltano config meltano set state_backend.uri "s3://your_bucket/meltano/state"

export MELTANO_STATE_BACKEND_URI="s3://your_bucket/meltano/state"
```

### <a name="state-backend-uri"></a>`state_backend.lock_timeout_seconds`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_BACKEND_LOCK_TIMEOUT_SECONDS`
- Default: `360`

Number of seconds that a [lock for a state ID](/concepts/state_backends#locking) should be considered valid in a state backend

#### How to use

```bash
meltano config meltano set state_backend.lock_timeout_seconds 720

export MELTANO_STATE_LOCK_TIMEOUT_SECONDS=720
```

### <a name="state-backend-uri"></a>`state_backend.lock_retry_seconds`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_BACKEND_LOCK_RETRY_SECONDS`
- Default: `360`

Number of seconds that a Meltano should wait if trying to access or modify state for a state ID that is [locked]((/concepts/state_backends#locking))

#### How to use

```bash
meltano config meltano set state_backend.lock_retry_seconds 720

export MELTANO_STATE_LOCK_RETRY_SECONDS=720
```

### Azure-Specific Settings
-----------------------------

### <a name="state-backend-uri"></a>`state_backend.azure.connection_string`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_AZURE_CONNECTION_STRING`
- Default: None

The [Azure connection string](https://learn.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string) to use when authenticating to Azure.

#### How to use

```bash
meltano config meltano set state_backend.azure.connection_string "DefaultEndpointsProtocol=https;AccountName=myAccountName;AccountKey=myAccountKey"

export MELTANO_STATE_BACKEND_AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myAccountName;AccountKey=myAccountKey"
```

### S3-Specific Settings
--------------------------

### <a name="state-backend-uri"></a>`state_backend.s3.aws_access_key_id`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_AWS_ACCESS_KEY_ID`
- Default: None

The AWS access key ID to use when authenticating to S3.

#### How to use

```bash
meltano config meltano set state_backend.s3.aws_access_key_id "someaccesskeyid"

export MELTANO_STATE_BACKEND_S3_AWS_ACCESS_KEY_ID="someaccesskeyid"
```

### <a name="state-backend-uri"></a>`state_backend.s3.aws_secret_access_key`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_AWS_SECRET_ACCESS_KEY`
- Default: None

The AWS secret access key to use when authenticating to S3.

#### How to use

```bash
meltano config meltano set state_backend.s3.aws_secret_access_key "somesecretaccesskey""

export MELTANO_STATE_BACKEND_S3_AWS_SECRET_ACCESS_KEY="somesecretaccesskey"
```

### <a name="state-backend-uri"></a>`state_backend.s3.endpoint_url`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_AWS_ENDPOINT_URL`
- Default: None

The endpoint URL to use when connecting to S3. Only necessary if using S3-compatible storage _not_ hosted by AWS (e.g. [Minio](https://min.io))

#### How to use

```bash
meltano config meltano set state_backend.s3.endpoint_url "https://play.min.io:9000""

export MELTANO_STATE_BACKEND_S3_ENDPOINT_URL="https://play.min.io:9000"
```

### GCS-Specific Settings
---------------------------

### <a name="state-backend-uri"></a>`state_backend.gcs.application_credentials`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_STATE_APPLICATION_CREDENTIALS`
- Default: None

Path to the [credential file](https://cloud.google.com/docs/authentication/application-default-credentials#GAC) to use in authenticating to Google Cloud Storage

#### How to use

```bash
meltano config meltano set state_backend.gcs.application_credentials "path/to/creds.json"

export MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS="path/to/creds.json"
```

## Snowplow Tracking

### `snowplow.collector_endpoints`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS`
- Default: `["https://sp.meltano.com"]`

Snowplow collector endpoints to be used if the [`send_anonymous_usage_stats` setting](#send-anonymous-usage-stats) is enabled. Events will be sent to all of these collectors.

## Feature Flags


### <a name="ff-enable-uvicron"></a>`ff.enable_uvicorn`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_FF_ENABLE_UVICORN`
- Default: `False`

### <a name="ff-strict-env-var-mode"></a>`ff.strict_env_var_mode`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_FF_STRICT_ENV_VAR_MODE`
- Default: `False`

Causes an exception to be raised if an environment variable is used within the project's Meltano configuration but that environment variable is not set.
