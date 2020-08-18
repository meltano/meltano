---
metaTitle: Configuring Meltano Settings
description: Manage a Meltano project's configuration using environment variables or `meltano.yml`.
sidebarDepth: 2
---

# Settings reference

As described in the [configuration guide](/docs/configuration.html#configuration-layers), Meltano will determine the values of these settings by first looking in **the environment**, then in a [**`.env` file**](https://github.com/theskumar/python-dotenv#usages) in your project directory, and finally in your project's **`meltano.yml` file**, falling back to a default value if nothing was found.

You can use [`meltano config meltano list`](/docs/command-line-interface.html#config) to list all available settings with their names, environment variables, and current values.

Configuration that is _not_ environment-specific or sensitive should be stored in your project's `meltano.yml` file and checked into version
control. Sensitive values like passwords and tokens are most appropriately stored in the environment, a (`.gitignore`d) `.env` file in your project directory, or the system database.

[`meltano config meltano set <setting> <value>`](/docs/command-line-interface.html#config), which is used in the examples below, will automatically store settings in `meltano.yml` or `.env` as appropriate.

## Plugin settings

For plugin settings, refer to the specific plugin's documentation
([extractors](/plugins/extractors/), [loaders](/plugins/loaders/)),
or use [`meltano config <plugin> list`](/docs/command-line-interface.html#config)
to list all available settings with their names, environment variables, and current values.

## Your Meltano project

These are settings specific to [your Meltano project](/docs/project.html).

### `send_anonymous_usage_stats`

- Environment variable: `MELTANO_SEND_ANONYMOUS_USAGE_STATS`, alias: `!MELTANO_DISABLE_TRACKING` (implies value `false`)
- [`meltano init`](/docs/command-line-interface.html#init) CLI flag: `--no_usage_stats` (implies value `false`)
- Default: `true`

By default, Meltano shares anonymous usage data with the Meltano team using Google Analytics. We use this data to learn about the size of our user base and the specific Meltano features they are (not yet) using, which helps us determine the highest impact changes we can make in each weekly release to make Meltano even more useful for you and others like you.

If enabled, Meltano will use the value of the [`project_id` setting](#project-id) to uniquely identify your project in Google Analytics.

If you'd like to send the tracking data to a different Google Analytics account than the one run by the Meltano team,
the Tracking IDs can be configured using the [`tracking_ids.*` settings](#analytics-tracking-ids) below.

If you'd prefer to use Meltano _without_ sending the team this kind of data, you can disable tracking entirely using one of these methods:

- When creating a new project, pass `--no_usage_stats` to [`meltano init`](/docs/command-line-interface.html#init)
- In an existing project, disable this `send_anonymous_usage_stats` setting
- To disable tracking in all projects in one go, enable the `MELTANO_DISABLE_TRACKING` environment variable

When anonymous usage tracking is enabled, Meltano tracks the following events:

- `meltano init {project name}`
- `meltano ui`
- `meltano elt {extractor} {loader} --transform {skip, only, run}`
- `meltano add {extractor, loader, transform, model, transformer, orchestrator}`
- `meltano discover {all, extractors, loaders, transforms, models, transformers, orchestrators}`
- `meltano install`
- `meltano invoke {plugin_name} {plugin_args}`
- `meltano select {extractor} {entities_filter} {attributes_filter}`
- `meltano schedule add {name} {extractor} {loader} {interval}`

Beyond the invocation of these commands and the identified command line arguments, Meltano does not track any other event metadata, plugin configuration, or processed data.

Finally, Meltano also tracks anonymous web metrics when browsing the Meltano UI pages.

#### How to use

```bash
meltano config meltano set send_anonymous_usage_stats false

export MELTANO_SEND_ANONYMOUS_USAGE_STATS=false
export MELTANO_DISABLE_TRACKING=true

meltano init --no_usage_stats demo-project
```

### `project_id`

- Environment variable: `MELTANO_PROJECT_ID`
- Default: None

Used by Meltano to uniquely identify your project in Google Analytics if the [`send_anonymous_usage_stats` setting](#send-anonymous-usage-stats) is enabled.

#### How to use

```bash
meltano config meltano set project_id <randomly-generated-token>

export MELTANO_PROJECT_ID=<randomly-generated-token>
```

### `database_uri`

- Environment variable: `MELTANO_DATABASE_URI`
- `meltano *` CLI flag: `--database-uri`
- Default: `sqlite:///$MELTANO_PROJECT_ROOT/.meltano/meltano.db`

Meltano stores pipeline state and other metadata in a project-specific system database,
which takes the shape of a SQLite database stored inside the project at `.meltano/meltano.db` by default.

You can choose to use a different system database backend or configuration using the `--database-uri`
option of [`meltano` subcommands](/docs/command-line-interface.html), or the `MELTANO_DATABASE_URI` environment variable.

#### How to use

```bash
meltano config meltano set database_uri postgresql://username:password@host:port/database

export MELTANO_DATABASE_URI=postgresql://username:password@host:port/database

meltano elt --database-uri=postgresql://username:password@host:port/database ...
```

### `project_readonly`

- Environment variable: `MELTANO_PROJECT_READONLY`
- Default: `false`

Enable this setting to indicate that your Meltano project is deployed as read-only,
and to block all modifications to project files through the [CLI](/docs/command-line-interface.md) and [UI](/docs/command-line-interface.md#ui)
in this environment.

Specifically, this prevents [adding plugins](/docs/command-line-interface.md#add) or [pipeline schedules](/docs/command-line-interface.md#schedule) to `meltano.yml`, as well as [modifying plugin configuration](/docs/command-line-interface.md#config) stored in `meltano.yml` or `.env`.

Note that [`meltano config <plugin> set`](/docs/command-line-interface.md#config) and [the UI](/docs/command-line-interface.md#ui)
can still be used to store configuration in the [system database](#database-uri),
but that settings that are already set in the environment or `meltano.yml` take precedence and cannot be overridden.

This setting differs from the [`ui.readonly` setting](#ui-readonly) in two ways:
1. it does not block write actions in the UI that do not modify project files, like storing settings in the system database, and
2. it also affects the [CLI](/docs/command-line-interface.md).

#### How to use

```bash
meltano config meltano set project_readonly true

export MELTANO_PROJECT_READONLY=true
```

### `discovery_url`

- Environment variable: `MELTANO_DISCOVERY_URL`
- Default: [`https://www.meltano.com/discovery.yml`](https://www.meltano.com/discovery.yml)

Where Meltano can find the `discovery.yml` manifest that lists all [known plugins](/docs/contributor-guide.html#known-plugins).

This manifest is used by [`meltano discover`](/docs/command-line-interface.md#discover) and [`meltano add`](/docs/command-line-interface.md#add), among others.

To disable downloading the remote `discovery.yml` manifest and only use the project-local or packaged version,
set this setting to `false` or any other string not starting with `http://` or `https://`.

#### How to use

```bash
meltano config meltano set discovery_url https://meltano.example.com/discovery.yml

export MELTANO_DISCOVERY_URL=https://meltano.example.com/discovery.yml
```

## `meltano` CLI

These settings can be used to modify the behavior of the [`meltano` CLI](/docs/command-line-interface.html).

### `cli.log_level`

- Environment variable: `MELTANO_CLI_LOG_LEVEL`, alias: `MELTANO_LOG_LEVEL`
- `meltano` CLI flag: `--log-level`
- Options: `debug`, `info`, `warning`, `error`, `critical`
- Default: `info`

The granularity of CLI logging.

#### How to use

```bash
meltano config meltano set cli log_level debug

export MELTANO_CLI_LOG_LEVEL=debug
export MELTANO_LOG_LEVEL=debug

meltano --log-level=debug ...
```

## Meltano UI server

These settings can be used to configure the [Meltano UI](/docs/command-line-interface.html#ui) server.

[Meltano UI feature settings](#meltano-ui-features) and [customization settings](#meltano-ui-customization) have their own sections.

### `ui.bind_host`

- Environment variable: `MELTANO_UI_BIND_HOST`, alias: `MELTANO_API_HOSTNAME`
- [`meltano ui`](/docs/command-line-interface.html#ui) CLI flag: `--bind`
- Default: `0.0.0.0`

The host to bind to.

Together with the [`ui.bind_port` setting](#ui-bind-port), this setting corresponds to
[Gunicorn's `bind` setting](https://docs.gunicorn.org/en/stable/settings.html#bind).

#### How to use

```bash
meltano config meltano set ui bind_host 127.0.0.1

export MELTANO_UI_BIND_HOST=127.0.0.1
export MELTANO_API_HOSTNAME=127.0.0.1

meltano ui --bind=127.0.0.1
```

### `ui.bind_port`

- Environment variable: `MELTANO_UI_BIND_PORT`, alias: `MELTANO_API_PORT`, `PORT`
- [`meltano ui`](/docs/command-line-interface.html#ui) CLI flag: `--bind-port`
- Default: `5000`

The port to bind to.

Together with the [`ui.bind_host` setting](#ui-bind-host), this setting corresponds to
[Gunicorn's `bind` setting](https://docs.gunicorn.org/en/stable/settings.html#bind).

#### How to use

```bash
meltano config meltano set ui bind_port 80

export MELTANO_UI_BIND_PORT=80
export MELTANO_API_PORT=80
export PORT=80

meltano ui --bind-port=80
```

### `ui.server_name`

- Environment variable: `MELTANO_UI_SERVER_NAME`
- Default: None

The host and port Meltano UI is available at.

Unless the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) is set, this setting will be used as the session cookie domain.

If the [`ui.notification` setting](#ui-notification) is enabled, this setting will be used to generate external URLs in notification emails.

When set, Meltano UI will only respond to requests whose hostname (`Host` header) matches this setting.
If this is undesirable, you can set the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) instead.
This may be the case when Meltano UI is situated behind a load balancer performing health checks without specifying a hostname.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/docs/command-line-interface.html#ui) will print a
security warning if neither this setting or the [`ui.session_cookie_domain` setting](#ui-session-cookie-domain) has been set.

This setting corresponds to [Flask's `SERVER_NAME` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SERVER_NAME).

#### How to use

```bash
meltano config meltano set ui server_name meltano.example.com

export MELTANO_UI_SERVER_NAME=meltano.example.com
```

[`meltano ui setup <server_name>`](/command-line-interface.html#setup) can be
used to generate secrets for the [`ui.secret_key`](#ui-secret-key) and
[`ui.password_salt`](#ui-password-salt) settings, that will be stored in a `.env`
file in your project directory along with the specified `server_name`.

```bash
meltano ui setup meltano.example.com
```

### `ui.session_cookie_domain`

- Environment variable: `MELTANO_UI_SESSION_COOKIE_DOMAIN`
- Default: None

The domain match rule that the session cookie will be valid for.

If not set, the cookie will be valid for all subdomains of the configured [`ui.server_name`](#ui-server-name).

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/docs/command-line-interface.html#ui) will print a
security warning if neither this setting or the [`ui.server_name` setting](#ui-server-name) has been set.

This setting corresponds to [Flask's `SESSION_COOKIE_DOMAIN` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_DOMAIN).

#### How to use

```bash
meltano config meltano set ui session_cookie_domain meltano.example.com

export MELTANO_UI_SESSION_COOKIE_DOMAIN=meltano.example.com
```

### `ui.secret_key`

- Environment variable: `MELTANO_UI_SECRET_KEY`
- Default: `thisisnotapropersecretkey`

A secret key that will be used for securely signing the session cookie.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/docs/command-line-interface.html#ui) will print a
security warning if this setting has not been changed from the default.

This setting corresponds to [Flask's `SECRET_KEY` setting](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY).

#### How to use

```bash
meltano config meltano set ui secret_key <randomly-generated-secret>

export MELTANO_UI_SECRET_KEY=<randomly-generated-secret>
```

[`meltano ui setup <server_name>`](/command-line-interface.html#setup) can be
used to generate secrets for the this setting and [`ui.password_salt`](#ui-password-salt),
that will be stored in a `.env` file in your project directory along with the specified [`ui.server_name`](#ui-server-name).

```bash
meltano ui setup meltano.example.com
```

### `ui.password_salt`

- Environment variable: `MELTANO_UI_PASSWORD_SALT`
- Default: `b4c124932584ad6e69f2774a0ae5c138`

The HMAC salt to use when hashing passwords.

If the [`ui.authentication` setting](#ui-authentication) is enabled,
[`meltano ui`](/docs/command-line-interface.html#ui) will print a
security warning if this setting has not been changed from the default.

This setting corresponds to [Flask-Security's `SECURITY_PASSWORD_SALT` setting](https://pythonhosted.org/Flask-Security/configuration.html).

#### How to use

```bash
meltano config meltano set ui password_salt <randomly-generated-secret>

export MELTANO_UI_PASSWORD_SALT=<randomly-generated-secret>
```

[`meltano ui setup <server_name>`](/command-line-interface.html#setup) can be
used to generate secrets for the this setting and [`ui.secret_key`](#ui-secret-key),
that will be stored in a `.env` file in your project directory along with the specified [`ui.server_name`](#ui-server-name).

```bash
meltano ui setup meltano.example.com
```

### `ui.workers`

- Environment variable: `MELTANO_UI_WORKERS`, alias: `WORKERS`, `WEB_CONCURRENCY`
- Default: `4`

The number of worker processes `meltano ui` will use to handle requests.

This setting corresponds to [Gunicorn's `workers` setting](https://docs.gunicorn.org/en/stable/settings.html#workers).

#### How to use

```bash
meltano config meltano set ui workers 1

export MELTANO_UI_WORKERS=1
export WORKERS=1
export WEB_CONCURRENCY=1
```

#### How to use

```bash
meltano config meltano set ui forwarded_allow_ips "*"

export MELTANO_UI_FORWARDED_ALLOW_IPS="*"
export FORWARDED_ALLOW_IPS="*"
```

### `ui.forwarded_allow_ips`

- Environment variable: `MELTANO_UI_FORWARDED_ALLOW_IPS`, alias: `FORWARDED_ALLOW_IPS`
- Default: `127.0.0.1`

Comma-separated front-end (reverse) proxy IPs that are allowed to set secure headers to indicate HTTPS requests.

Set to `*` to disable checking of front-end IPs, which can be useful for setups where you don't know in advance the IP address of front-end, but you still trust the environment.

This setting corresponds to [Gunicorn's `forwarded_allow_ips` setting](https://docs.gunicorn.org/en/stable/settings.html#forwarded-allow-ips).

## Meltano UI features

These settings can be used to enable certain features of [Meltano UI](/docs/command-line-interface.html#ui).

[Meltano UI server settings](#meltano-ui-server) and [customization settings](#meltano-ui-customization) have their own sectionss

### `ui.readonly`

- Environment variable: `MELTANO_UI_READONLY`, alias: `MELTANO_READONLY`
- Default: `false`

To block all write actions in the Meltano UI, you can run it in in *read-only* mode.

If you're enabling the [`ui.authentication` setting](#ui-authentication) and would
like to only use read-only mode for anonymous users, enable the [`ui.anonymous_readonly` setting](#ui-anonymous-readonly) instead.

This setting differs from the [`project_readonly` setting](#project-readonly) in two ways:
1. it also blocks write actions in the UI that do not modify project files, like storing settings in the system database, and
2. it does not affect the [CLI](/docs/command-line-interface.md).

#### How to use

```bash
meltano config meltano set ui readonly true

export MELTANO_UI_READONLY=true
export MELTANO_READONLY=true
```

### `ui.authentication`

- Environment variable: `MELTANO_UI_AUTHENTICATION`, alias: `MELTANO_AUTHENTICATION`
- Default: `false`

Use this setting to enable authentication and disallow anonymous usage of your Meltano instance.

Additionally, you will need to:
1. Ensure your configuration is secure by setting the [`ui.secret_key`](#ui-secret-key) and [`ui.password_salt`](#ui-password-salt) settings, as well as [`ui.server_name`](#ui-server-name) or [`ui.session_cookie_domain`](#ui-session-cookie-domain), manually or using [`meltano ui setup <server_name>`](./command-line-interface.html#setup).

2. Create at least one user using [`meltano user add`](./command-line-interface.html#user).

#### How to use

```bash
meltano config meltano set ui authentication true

export MELTANO_UI_AUTHENTICATION=true
export MELTANO_AUTHENTICATION=true
```

### `ui.anonymous_readonly`

- Environment variable: `MELTANO_UI_ANONYMOUS_READONLY`
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

### `ui.notification`

- Environment variable: `MELTANO_UI_NOTIFICATION`, alias: `MELTANO_NOTIFICATION`
- Default: `false`

Meltano can send email notifications upon certain events.

Your outgoing mail server can be configured using the [`mail.*` settings](#mail-server) below.

::: tip
To ease the development and testing, Meltano is preconfigured to use a local [MailHog](https://github.com/mailhog) instance to trap all the outgoing emails.

Use the following docker command to start it:

```bash
docker run --rm -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
```

All emails sent by Meltano should now be available at `http://localhost:8025/`
:::

#### How to use

```bash
meltano config meltano set ui notification true

export MELTANO_UI_NOTIFICATION=true
export MELTANO_NOTIFICATION=true
```

### `ui.analysis`

- Environment variable: `MELTANO_UI_ANALYSIS`
- Default: `true`

If you are only using Meltano for data integration (and transformation),
you can disable this setting to hide all functionality related to Analysis from the UI:
- "Explore" and "Dashboards" tabs
- "Explore" buttons in the "Pipelines" list and "Pipeline Run Log" modal

#### How to use

```bash
meltano config meltano set ui analysis false

export MELTANO_UI_ANALYSIS=true
```

## Meltano UI customization

These settings can be used to customize certain aspects of [Meltano UI](/docs/command-line-interface.html#ui).

[Meltano UI server settings](#meltano-ui-server) and [feature settings](#meltano-ui-features) have their own sections.

### `ui.logo_url`

- Environment variable: `MELTANO_UI_LOGO_URL`
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

- Environment variable: `MAIL_SERVER`
- Default: `localhost`

```bash
meltano config meltano set mail server smtp.example.com

export MAIL_SERVER=smtp.example.com
```

### `mail.port`

- Environment variable: `MAIL_PORT`
- Default: `1025`

```bash
meltano config meltano set mail port 25

export MAIL_PORT=25
```

### `mail.default_sender`

- Environment variable: `MAIL_DEFAULT_SENDER`
- Default: `"Meltano" <bot@meltano.com>`

```bash
meltano config meltano set mail default_sender '"Example Meltano" <bot@meltano.example.com>'

export MAIL_DEFAULT_SENDER='"Example Meltano" <bot@meltano.example.com>'
```

### `mail.use_tls`

- Environment variable: `MAIL_USE_TLS`
- Default: `false`

```bash
meltano config meltano set mail use_tls true

export MAIL_USE_TLS=true
```

### `mail.username`

- Environment variable: `MAIL_USERNAME`
- Default: None

```bash
meltano config meltano set mail username meltano

export MAIL_USERNAME=meltano
```

### `mail.password`

- Environment variable: `MAIL_PASSWORD`
- Default: None

```bash
meltano config meltano set mail password meltano

export MAIL_PASSWORD=meltano
```

### `mail.debug`

- Environment variable: `MAIL_DEBUG`
- Default: `false`

```bash
meltano config meltano set mail debug true

export MAIL_DEBUG=true
```

## OAuth Service

Meltano ships with an OAuth Service to handle the OAuth flow in the Extractors' configuration.

::: warning
To run this service, you **must** have a registered OAuth application on the [Authorization server](https://www.oauth.com/oauth2-servers/definitions/#the-authorization-server).

Most importantly, the Redirect URI must be set properly so that the OAuth flow can be completed.

This process is specific to each Provider.
:::

The OAuth Service is bundled within Meltano, and is automatically started with [`meltano ui`](/docs/command-line-interface.html#ui) and mounted at `/-/oauth` for development purposes.

As it is a Flask application, it can also be run as a standalone using:

```bash
FLASK_ENV=production FLASK_APP=meltano.oauth python -m flask run --port 9999
```

### `oauth_service.url`

- Environment variable: `MELTANO_OAUTH_SERVICE_URL`
- Default: None

Meltano provides a public hosted solution at <https://oauth.svc.meltanodata.com>.

The local OAuth service for development purposes is available at `/-/oauth`.

#### How to use

```bash
meltano config meltano set oauth_service url https://oauth.svc.meltanodata.com

export MELTANO_OAUTH_SERVICE_URL=https://oauth.svc.meltanodata.com
```

### `oauth_service.providers`

- Environment variable: `MELTANO_OAUTH_SERVICE_PROVIDERS`
- Default: `all`

To enable specific providers, use comma-separated `oauth.provider` names from `discovery.yml`. To enable all providers, use `all`.

#### How to use

```bash
meltano config meltano set oauth_service providers facebook,google_adwords

export MELTANO_OAUTH_SERVICE_PROVIDERS=facebook,google_adwords
```

### `oauth_service.facebook.client_id`

- Environment variable: `OAUTH_FACEBOOK_CLIENT_ID`
- Default: None

```bash
meltano config meltano set oauth_service facebook client_id <facebook-client-id>

export OAUTH_FACEBOOK_CLIENT_ID=<facebook-client-id>
```

### `oauth_service.facebook.client_secret`

- Environment variable: `OAUTH_FACEBOOK_CLIENT_SECRET`
- Default: None

```bash
meltano config meltano set oauth_service facebook client_secret <facebook-client-secret>

export OAUTH_FACEBOOK_CLIENT_SECRET=<facebook-client-secret>
```

### `oauth_service.google_adwords.client_id`

- Environment variable: `OAUTH_GOOGLE_ADWORDS_CLIENT_ID`
- Default: None

```bash
meltano config meltano set oauth_service google_adwords client_id <google-adwords-client-id>

export OAUTH_GOOGLE_ADWORDS_CLIENT_ID=<google-adwords-client-id>
```

### `oauth_service.google_adwords.client_secret`

- Environment variable: `OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET`
- Default: None

```bash
meltano config meltano set oauth_service google_adwords client_secret <google-adwords-client-secret>

export OAUTH_GOOGLE_ADWORDS_CLIENT_SECRET=<google-adwords-client-secret>
```

## OAuth Single-Sign-On

These variables are specific to [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/#) and work with [OAuth authentication with GitLab](https://docs.gitlab.com/ee/integration/oauth_provider.html).

::: tip
These settings are used for single-sign-on using an external OAuth provider.
:::

For more information on how to get these from your GitLab application, check out the [integration docs from GitLab](https://docs.gitlab.com/ee/integration/gitlab.html).

### `oauth.gitlab.client_id`

- Environment variable: `OAUTH_GITLAB_CLIENT_ID`, alias: `OAUTH_GITLAB_APPLICATION_ID`
- Default: None

```bash
meltano config meltano set oauth gitlab client_id <gitlab-client-id>

export OAUTH_GITLAB_CLIENT_ID=<gitlab-client-id>
export OAUTH_GITLAB_APPLICATION_ID=<gitlab-client-id>
```

### `oauth.gitlab.client_secret`

- Environment variable: `OAUTH_GITLAB_CLIENT_SECRET`, alias: `OAUTH_GITLAB_SECRET`
- Default: None

```bash
meltano config meltano set oauth gitlab client_secret <gitlab-client-secret>

export OAUTH_GITLAB_CLIENT_SECRET=<gitlab-client-secret>
export OAUTH_GITLAB_SECRET=<gitlab-client-secret>
```

## Analytics Tracking IDs

Google Analytics Tracking IDs to be used if the [`send_anonymous_usage_stats` setting](#send-anonymous-usage-stats) is enabled.

### `tracking_ids.cli`

- Environment variable: `MELTANO_TRACKING_IDS_CLI`, alias: `MELTANO_CLI_TRACKING_ID`
- Default: `UA-132758957-3`

Tracking ID for usage of the [`meltano` CLI](/docs/command-line-interface.html).

```bash
meltano config meltano set tracking_ids cli UA-123456789-1

export MELTANO_TRACKING_IDS_CLI=UA-123456789-1
export MELTANO_CLI_TRACKING_ID=UA-123456789-1
```

### `tracking_ids.ui`

- Environment variable: `MELTANO_TRACKING_IDS_UI`, alias: `MELTANO_UI_TRACKING_ID`
- Default: `UA-132758957-2`

Tracking ID for usage of [Meltano UI](/docs/command-line-interface.html#ui).

```bash
meltano config meltano set tracking_ids ui UA-123456789-2

export MELTANO_TRACKING_IDS_UI=UA-123456789-2
export MELTANO_UI_TRACKING_ID=UA-123456789-2
```

### `tracking_ids.ui_embed`

- Environment variable: `MELTANO_TRACKING_IDS_UI_EMBED`, alias: `MELTANO_EMBED_TRACKING_ID`
- Default: `UA-132758957-6`

Tracking ID for usage of [Meltano UI](/docs/command-line-interface.html#ui)'s [Embed feature](/docs/analysis.html#share-reports-and-dashboards).

```bash
meltano config meltano set tracking_ids ui_embed UA-123456789-3

export MELTANO_TRACKING_IDS_UI_EMBED=UA-123456789-3
export MELTANO_EMBED_TRACKING_ID=UA-123456789-3
```
