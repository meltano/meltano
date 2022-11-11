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

Meltano also tracks anonymous web metrics when browsing the Meltano UI pages.

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

Note that [`meltano config <plugin> set`](/reference/command-line-interface#config) and [the UI](/reference/ui)
can still be used to store configuration in the [system database](/concepts/project#system-database),
but that settings that are already [set in the environment](/guide/configuration#configuring-settings) or `meltano.yml` take precedence and cannot be overridden.

This setting differs from the [`ui.readonly` setting](#ui-readonly) in two ways:

1. it does not block write actions in the UI that do not modify project files, like storing settings in the [system database](/concepts/project#system-database), and
2. it also affects the [CLI](/reference/command-line-interface).

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

## Meltano UI server

These settings can be used to configure the [Meltano UI](/reference/ui) server.

[Meltano UI feature settings](#meltano-ui-features) and [customization settings](#meltano-ui-customization) have their own sections.

### <a name="ui-bind-host"></a>`ui.bind_host`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_BIND_HOST`
- [`meltano ui`](/reference/command-line-interface#ui) CLI option: `--bind`
- Default: `0.0.0.0`

The host to bind to.

Together with the [`ui.bind_port` setting](#ui-bind-port), this setting corresponds to
[Gunicorn's `bind` setting](https://docs.gunicorn.org/en/stable/settings.html#bind).

#### How to use

```bash
meltano config meltano set ui bind_host 127.0.0.1

export MELTANO_UI_BIND_HOST=127.0.0.1

meltano ui --bind=127.0.0.1
```

### <a name="ui-bind-port"></a>`ui.bind_port`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_BIND_PORT`
- [`meltano ui`](/reference/command-line-interface#ui) CLI option: `--bind-port`
- Default: `5000`

The port to bind to.

Together with the [`ui.bind_host` setting](#ui-bind-host), this setting corresponds to
[Gunicorn's `bind` setting](https://docs.gunicorn.org/en/stable/settings.html#bind).

#### How to use

```bash
meltano config meltano set ui bind_port 80

export MELTANO_UI_BIND_PORT=80

meltano ui --bind-port=80
```

### <a name="ui-server-name"></a>`ui.server_name`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_SERVER_NAME`
- Default: None

The host and port Meltano UI is available at, e.g. `<host>:<port>`.

The port will usually match the [`ui.bind_port` setting](#ui-bind-port), and can be omitted when the default port for HTTP (`80`) or HTTPS (`443`) is used.

Unless the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) is set, this setting will be used as the session cookie domain.

If the [`ui.notification` setting](#ui-notification) is enabled, this setting will be used to generate external URLs in notification emails.

When set, Meltano UI will only respond to requests whose hostname (`Host` header) matches this setting.
If this is undesirable, you can set the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) instead.
This may be the case when Meltano UI is situated behind a load balancer performing health checks without specifying a hostname.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/reference/command-line-interface#ui) will print a
security warning if neither this setting or the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) has been set.

This setting corresponds to [Flask's `SERVER_NAME` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SERVER_NAME).

#### How to use

```bash
meltano config meltano set ui server_name meltano.example.com

export MELTANO_UI_SERVER_NAME=meltano.example.com
```

[`meltano ui setup <server_name>`](/reference/command-line-interface#setup) can be
used to generate secrets for the [`ui.secret_key`](#ui-secret-key) and
[`ui.password_salt`](#ui-password-salt) settings, that will be stored in a
your project's [`.env` file](/concepts/project#env) along with the specified `server_name`.

```bash
meltano ui setup meltano.example.com
```

### <a name="ui-session-cookie-domain"></a>`ui.session_cookie_domain`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_SESSION_COOKIE_DOMAIN`
- Default: None

The domain match rule that the session cookie will be valid for.

If not set, the cookie will be valid for all subdomains of the configured [`ui.server_name`](#ui-server-name).

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/reference/command-line-interface#ui) will print a
security warning if neither this setting or the [`ui.server_name` setting](#ui-server-name) has been set.

This setting corresponds to [Flask's `SESSION_COOKIE_DOMAIN` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_DOMAIN).

#### How to use

```bash
meltano config meltano set ui session_cookie_domain meltano.example.com

export MELTANO_UI_SESSION_COOKIE_DOMAIN=meltano.example.com
```

### <a name="ui-session-cookie-secure"></a>`ui.session_cookie_secure`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_SESSION_COOKIE_SECURE`
- Default: `false`

Enable the `Secure` flag on the session cookie, so that the client will only send it to the server in HTTPS requests.

The application must be served over HTTPS for this to make sense.

This setting corresponds to [Flask's `SESSION_COOKIE_SECURE` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_SECURE).

#### How to use

```bash
meltano config meltano set ui session_cookie_secure true

export MELTANO_UI_SESSION_COOKIE_SECURE=true
```

### <a name="ui-secret-key"></a>`ui.secret_key`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_SECRET_KEY`
- Default: `thisisnotapropersecretkey`

A secret key that will be used for securely signing the session cookie.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/reference/command-line-interface#ui) will print a
security warning if this setting has not been changed from the default.

This setting corresponds to [Flask's `SECRET_KEY` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY).

#### How to use

```bash
meltano config meltano set ui secret_key <randomly-generated-secret>

export MELTANO_UI_SECRET_KEY=<randomly-generated-secret>
```

[`meltano ui setup <server_name>`](/reference/command-line-interface#setup) can be
used to generate secrets for the this setting and [`ui.password_salt`](#ui-password-salt),
that will be stored in your project's [`.env` file](/concepts/project#env)
along with the specified [`ui.server_name`](#ui-server-name).

```bash
meltano ui setup meltano.example.com
```

### <a name="ui-password-salt"></a>`ui.password_salt`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_PASSWORD_SALT`
- Default: `b4c124932584ad6e69f2774a0ae5c138`

The HMAC salt to use when hashing passwords.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/reference/command-line-interface#ui) will print a
security warning if this setting has not been changed from the default.

This setting corresponds to [Flask-Security's `SECURITY_PASSWORD_SALT` setting](https://pythonhosted.org/Flask-Security/configuration.html).

#### How to use

```bash
meltano config meltano set ui password_salt <randomly-generated-secret>

export MELTANO_UI_PASSWORD_SALT=<randomly-generated-secret>
```

[`meltano ui setup <server_name>`](/reference/command-line-interface#setup) can be
used to generate secrets for the this setting and [`ui.secret_key`](#ui-secret-key),
that will be stored in your project's [`.env` file](/concepts/project#env)
along with the specified [`ui.server_name`](#ui-server-name).

```bash
meltano ui setup meltano.example.com
```

### `ui.workers`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_WORKERS`
- Default: `4`

The number of worker processes `meltano ui` will use to handle requests.

This setting corresponds to [Gunicorn's `workers` setting](https://docs.gunicorn.org/en/stable/settings.html#workers).

#### How to use

```bash
meltano config meltano set ui workers 1

export MELTANO_UI_WORKERS=1
```

### <a name="ui-forwarded-allow-ips"></a>`ui.forwarded_allow_ips`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_FORWARDED_ALLOW_IPS`
- Default: `127.0.0.1`

Comma-separated front-end (reverse) proxy IPs that are allowed to set secure headers to indicate HTTPS requests.

Set to `*` to disable checking of front-end IPs, which can be useful for setups where you don't know in advance the IP address of front-end, but you still trust the environment.

This setting corresponds to [Gunicorn's `forwarded_allow_ips` setting](https://docs.gunicorn.org/en/stable/settings.html#forwarded-allow-ips).

#### How to use

```bash
meltano config meltano set ui forwarded_allow_ips "*"

export MELTANO_UI_FORWARDED_ALLOW_IPS="*"
```

## Meltano UI features

These settings can be used to enable certain features of [Meltano UI](/reference/ui).

[Meltano UI server settings](#meltano-ui-server) and [customization settings](#meltano-ui-customization) have their own sectionss

### <a name="ui-readonly"></a>`ui.readonly`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_READONLY`
- Default: `false`

To block all write actions in the Meltano UI, you can run it in in _read-only_ mode.

If you're enabling the [`ui.authentication` setting](#ui-authentication) and would
like to only use read-only mode for anonymous users, enable the [`ui.anonymous_readonly` setting](#ui-anonymous-readonly) instead.

This setting differs from the [`project_readonly` setting](#project-readonly) in two ways:

1. it also blocks write actions in the UI that do not modify project files, like storing settings in the [system database](/concepts/project#system-database), and
2. it does not affect the [CLI](/reference/command-line-interface).

#### How to use

```bash
meltano config meltano set ui readonly true

export MELTANO_UI_READONLY=true
```

### <a name="ui-authentication"></a>`ui.authentication`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_AUTHENTICATION`
- Default: `false`

Use this setting to enable authentication and disallow anonymous usage of your Meltano instance.

Additionally, you will need to:

1. Ensure your configuration is secure by setting the [`ui.secret_key`](#ui-secret-key) and [`ui.password_salt`](#ui-password-salt) settings, as well as [`ui.server_name`](#ui-server-name) or [`ui.session_cookie_domain`](#ui-session-cookie-domain), manually or using [`meltano ui setup <server_name>`](./command-line-interface.html#setup).

2. Create at least one user using [`meltano user add`](./command-line-interface.html#user).

#### How to use

```bash
meltano config meltano set ui authentication true

export MELTANO_UI_AUTHENTICATION=true
```

### <a name="ui-anonymous-readonly"></a>`ui.anonymous_readonly`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_ANONYMOUS_READONLY`
- Default: `false`

When the [`ui.authentication` setting](#ui-authentication) is enabled,
enabling this setting will allow anonymous users read-only access to Meltano UI.
Once a user is authenticated, write actions will be available again.

This setting is especially useful when setting up a publicly available demo
instance of Meltano UI for anonymous users to interact with.
These users will not be able to make any changes, but admins will once they sign in.

#### How to use

```bash
meltano config meltano set ui anonymous_readonly true

export MELTANO_UI_ANONYMOUS_READONLY=true
```

### <a name="ui-notification"></a>`ui.notification`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_NOTIFICATION`
- Default: `false`

Meltano can send email notifications upon certain events.

Your outgoing mail server can be configured using the [`mail.*` settings](#mail-server) below.

<div class="notification is-info">
  <p>To ease the development and testing, Meltano is preconfigured to use a local <a href="https://github.com/mailhog">MailHog</a> instance to trap all the outgoing emails.</p>
  <p>Use the following docker command to start it:</p>
<pre>
docker run --rm -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
</pre>
  <p>All emails sent by Meltano should now be available at <code>http://localhost:8025/</code></p>
</div>

#### How to use

```bash
meltano config meltano set ui notification true

export MELTANO_UI_NOTIFICATION=true
```

## Meltano UI customization

These settings can be used to customize certain aspects of [Meltano UI](/reference/ui).

[Meltano UI server settings](#meltano-ui-server) and [feature settings](#meltano-ui-features) have their own sections.

### `ui.logo_url`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_UI_LOGO_URL`
- Default: None

Customize the logo used by Meltano UI in the navigation bar and on the sign-in page (when the [`ui.authentication` setting](#ui-authentication) is enabled).

#### How to use

```bash
meltano config meltano set ui logo_url https://meltano.com/meltano-logo-with-text.svg

export MELTANO_UI_LOGO_URL=https://meltano.com/meltano-logo-with-text.svg
```

## Mail server

Meltano uses [Flask-Mail](https://pythonhosted.org/Flask-Mail/) to send emails. Take a look at the documentation to properly configure your outgoing email server.

### `mail.server`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_SERVER`
- Default: `localhost`

```bash
meltano config meltano set mail server smtp.example.com

export MELTANO_MAIL_SERVER=smtp.example.com
```

### `mail.port`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_PORT`
- Default: `1025`

```bash
meltano config meltano set mail port 25

export MELTANO_MAIL_PORT=25
```

### `mail.default_sender`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_DEFAULT_SENDER`
- Default: `"Meltano" <bot@meltano.com>`

```bash
meltano config meltano set mail default_sender '"Example Meltano" <bot@meltano.example.com>'

export MELTANO_MAIL_DEFAULT_SENDER='"Example Meltano" <bot@meltano.example.com>'
```

### `mail.use_tls`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_USE_TLS`
- Default: `false`

```bash
meltano config meltano set mail use_tls true

export MELTANO_MAIL_USE_TLS=true
```

### `mail.username`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_USERNAME`
- Default: None

```bash
meltano config meltano set mail username meltano

export MELTANO_MAIL_USERNAME=meltano
```

### `mail.password`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_PASSWORD`
- Default: None

```bash
meltano config meltano set mail password meltano

export MELTANO_MAIL_PASSWORD=meltano
```

### `mail.debug`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_DEBUG`
- Default: `false`

```bash
meltano config meltano set mail debug true

export MELTANO_MAIL_DEBUG=true
```

### `mail.sendgrid_unsubscribe_group_id`

If you are using the SendGrid SMTP API you may optionally set the [SendGrid unsubscribe group ID](https://docs.sendgrid.com/ui/sending-email/unsubscribe-groups).

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_MAIL_SENDGRID_UNSUBSCRIBE_GROUP_ID`
- Default: `12751`

```bash
meltano config meltano set mail sendgrid_unsubscribe_group_id 42

export MELTANO_MAIL_SENDGRID_UNSUBSCRIBE_GROUP_ID=42
```

## OAuth Service

Meltano ships with an OAuth Service to handle the OAuth flow in the Extractors' configuration.

<div class="notification is-warning">
  <p>To run this service, you **must** have a registered OAuth application on the [Authorization server](https://www.oauth.com/oauth2-servers/definitions/#the-authorization-server).</p>
  <p>Most importantly, the Redirect URI must be set properly so that the OAuth flow can be completed.</p>
  <p>This process is specific to each Provider.</p>
</div>

The OAuth Service is bundled within Meltano, and is automatically started with [`meltano ui`](/reference/command-line-interface#ui) and mounted at `/-/oauth` for development purposes.

As it is a Flask application, it can also be run as a standalone using:

```bash
FLASK_ENV=production FLASK_APP=meltano.oauth python -m flask run --port 9999
```

### `oauth_service.url`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_OAUTH_SERVICE_URL`
- Default: None

The local OAuth service for development purposes is available at `/-/oauth`.

#### How to use

```bash
meltano config meltano set oauth_service url https://oauth.svc.meltanodata.com

export MELTANO_OAUTH_SERVICE_URL=https://oauth.svc.meltanodata.com
```

### `oauth_service.providers`

- [Environment variable](/guide/configuration#configuring-settings): `MELTANO_OAUTH_SERVICE_PROVIDERS`
- Default: `all`

To enable specific providers, use comma-separated `oauth.provider` names from `discovery.yml`. To enable all providers, use `all`.

#### How to use

```bash
meltano config meltano set oauth_service providers facebook,google_adwords

export MELTANO_OAUTH_SERVICE_PROVIDERS=facebook,google_adwords
```

### `oauth_service.facebook.client_id`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_FACEBOOK_CLIENT_ID`
- Default: None

```bash
meltano config meltano set oauth_service facebook client_id <facebook-client-id>

export OAUTH_FACEBOOK_CLIENT_ID=<facebook-client-id>
```

### `oauth_service.facebook.client_secret`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_FACEBOOK_CLIENT_SECRET`
- Default: None

```bash
meltano config meltano set oauth_service facebook client_secret <facebook-client-secret>

export OAUTH_FACEBOOK_CLIENT_SECRET=<facebook-client-secret>
```

### `oauth_service.google_adwords.client_id`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_GOOGLE_ADWORDS_CLIENT_ID`
- Default: None

```bash
meltano config meltano set oauth_service google_adwords client_id <google-adwords-client-id>

export OAUTH_GOOGLE_ADWORDS_CLIENT_ID=<google-adwords-client-id>
```

### `oauth_service.google_adwords.client_secret`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET`
- Default: None

```bash
meltano config meltano set oauth_service google_adwords client_secret <google-adwords-client-secret>

export OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET=<google-adwords-client-secret>
```

## OAuth Single-Sign-On

These variables are specific to [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/#) and work with [OAuth authentication with GitLab](https://docs.gitlab.com/ee/integration/oauth_provider.html).

<div class="notification is-info">
  <p>These settings are used for single-sign-on using an external OAuth provider.</p>
</div>

For more information on how to get these from your GitLab application, check out the [integration docs from GitLab](https://docs.gitlab.com/ee/integration/gitlab.html).

### `oauth.gitlab.client_id`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_GITLAB_CLIENT_ID`, alias: `OAUTH_GITLAB_APPLICATION_ID`
- Default: None

```bash
meltano config meltano set oauth gitlab client_id <gitlab-client-id>

export OAUTH_GITLAB_CLIENT_ID=<gitlab-client-id>
export OAUTH_GITLAB_APPLICATION_ID=<gitlab-client-id>
```

### `oauth.gitlab.client_secret`

- [Environment variable](/guide/configuration#configuring-settings): `OAUTH_GITLAB_CLIENT_SECRET`, alias: `OAUTH_GITLAB_SECRET`
- Default: None

```bash
meltano config meltano set oauth gitlab client_secret <gitlab-client-secret>

export OAUTH_GITLAB_CLIENT_SECRET=<gitlab-client-secret>
export OAUTH_GITLAB_SECRET=<gitlab-client-secret>
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
