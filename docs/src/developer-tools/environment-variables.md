---
sidebarDepth: 2
---

# Environment Variables

For each Meltano installation, if you need to customize environment variables, this is done with the `.env` file that is created with each new installation.

## Anonymous Usage Data

By default, Meltano shares anonymous usage data with the Meltano team using Google Analytics. We use this data to learn about the size of our user base and the specific Meltano features they are (not yet) using, which helps us determine the highest impact changes we can make in each weekly release to make Meltano even more useful for you and others like you.

If you'd prefer to use Meltano _without_ sending the team this kind of data, you can disable tracking entirely using one of these methods:

- When creating a new project, pass `--no_usage_stats` to `meltano init`:

  ```bash
  meltano init PROJECT_NAME --no_usage_stats
  ```

- In an existing project, disable the `send_anonymous_usage_stats` setting in the `meltano.yml` file:

  ```bash
  send_anonymous_usage_stats: false
  ```

- To disable tracking in all projects in one go, set the `MELTANO_DISABLE_TRACKING` environment variable to `True`:

  ```bash
  # Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
  export MELTANO_DISABLE_TRACKING=True
  ```

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
- `meltano permissions grant --db {postgres, snowflake} --dry`

Beyond the invocation of these commands and the identified command line arguments, Meltano does not track any other event metadata, plugin configuration, or processed data.

Finally, Meltano also tracks anonymous web metrics when browsing the Meltano UI pages.

If you want to evaluate Meltano's anonymous usage tracking strategy for yourself, you can check [meltano.core.tracking.GoogleAnalyticsTracker](https://gitlab.com/meltano/meltano/blob/master/src/meltano/core/tracking/ga_tracker.py) and all the places that it is used.


## Connector Settings Configuration

Until role-based access control is implemented in Meltano, we need to prevent user editing of certain settings from the UI. View this [`tap-gitlab` environment variable setup example](/tutorials/gitlab-and-postgres.html#add-extractor) to learn how to work with this current limitation.

## Meltano UI

### System Database

By default, Meltano uses a SQLite database named `./meltano/meltano.db` as its system database.

You can choose to use a different system database backend or configuration using the `--database-uri`
option of the `meltano` command, or the `MELTANO_DATABASE_URI` environment variable:

```bash
 SQLite (absolute path required, notice the `3` slashes before the path)
export MELTANO_DATABASE_URI=sqlite:////path/to/system_database.db
 PostgreSQL:
export MELTANO_DATABASE_URI=postgresql://username:password@host:port/database
```

### Flask

The following are the environment variables currently available for customization for Flask.

Update your `.env` file in your project directory with the desired customizations.

```bash
export FLASK_PROFILE = ""
export FLASK_ENV = ""
```

#### Service Listen Configuration

By default, the API service listens with following host/port combination.

API: `http://0.0.0.0:5000`

To change the host/port configuration on which the API server listens, update your `.env` in your project directory with the following configuration:

```bash
 Meltano API configuration
export MELTANO_API_HOSTNAME="0.0.0.0"
export MELTANO_API_PORT="5000"
```

#### Single Sign On

These variables are specific to [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/#) and work with [OAuth authentication with GitLab](https://docs.gitlab.com/ee/integration/oauth_provider.html).

::: tip
These settings are used for single-sign-on using an external OAuth provider.
:::

Update your `.env` file in your project directory with the desired customizations.

```bash
 GitLab Client ID
export OAUTH_GITLAB_APPLICATION_ID = ""
 GitLab Client Secret
export OAUTH_GITLAB_SECRET = ""
```

For more information on how to get these from your GitLab application, check out the [integration docs from GitLab](https://docs.gitlab.com/ee/integration/gitlab.html).

### Read-Only mode

The disable all modifications to the Meltano UI, you can run Meltano using the *read-only* mode.

```bash
 Meltano read-only mode
export MELTANO_READONLY=1
```

### OAuth Service

::: tip
Meltano provides a public hosted solution at <https://oauth.svc.meltanodata.com>.
:::

```bash
 use the public OAuth Service
MELTANO_OAUTH_SERVICE_URL=https://oauth.svc.meltanodata.com

 use the local OAuth Service
MELTANO_OAUTH_SERVICE_URL=http://localhost:5000/-/oauth
```

## Meltano OAuth Service

Meltano ships with an OAuth Service to handle the OAuth flow in the Extractors' configuration.

::: warning
To run this service, you **must** have a registered OAuth application on the [Authorization server](https://www.oauth.com/oauth2-servers/definitions/#the-authorization-server).

Most importantly, the Redirect URI must be set properly so that the OAuth flow can be completed.

This process is specific to each Provider.
:::

### Starting the service

The OAuth Service is bundled within Meltano, and is automatically started with `meltano ui` and mounted at `/-/oauth` for development purposes.

As it is a Flask application, it can also be run as a standalone using:

```bash
FLASK_ENV=production FLASK_APP=meltano.oauth python -m flask run --port 9999
```

### Providers configuration

#### Facebook

```bash
OAUTH_FACEBOOK_CLIENT_ID=<application_id>
OAUTH_FACEBOOK_CLIENT_SECRET=<application_secret>
```

