# Meltano Cloud CLI

`meltano-cloud` is a standalone CLI tool for interacting with the Meltano Cloud API. It is also available as a subcommand of `meltano`, i.e. `meltano cloud`.

### Configuration File

Meltano Cloud configuration settings and credentials are stored in a JSON file. The CLI searches for this configuration file in standard locations using [`platformdirs`](https://github.com/platformdirs/platformdirs).

If a configuration file is found but the configuration it contains is invalid, the CLI will raise an error rather than continuing its search.

### Settings

The following settings are configurable:

#### `auth_callback_port`

As part of authentication, the CLI runs a lightweight, short-lived HTTP server on `localhost` to handle authentication callbacks. By default, this server runs on port 9999 but can be configured to another port using this setting.

- Command line flag: `--auth-callback-port`
- Environment variable: `MELTANO_CLOUD_AUTH_CALLBACK_PORT`

#### `base_url`

This is the base URL used for API calls to Meltano Cloud, `https://api.meltano.cloud` by default.

- Command line flag: `--base-url`
- Environment variable: `MELTANO_CLOUD_BASE_URL`

#### `base_auth_url`

This is the base URL used for authentication calls to Meltano Cloud, `https://auth.meltano.cloud` by default.

- Command line flag: `--base-auth-url`
- Environment variable: `MELTANO_CLOUD_BASE_AUTH_URL`

#### `organization_id`

This is the default ID for the Meltano Cloud organization to use in interacting with the Meltano Cloud API.

- Command line flag: `--organization-id`
- Environment variable: `MELTANO_CLOUD_ORGANIZATION_ID`

#### `project_id`

For project-specific commands, this is the project ID to use by default in interacting with the Meltano Cloud API.

- Command line flag: `--project-id`
- Environment variable: `MELTANO_CLOUD_PROJECT_ID`

### Setting Value Resolution

The Meltano Cloud CLI resolves configuration setting values as follows (from highest to lowest precedence):

- A value provided by a command-line flag, for example
  `--project-id <project_id>`.
- A value provided by an environment variable, for example `MELTANO_CLOUD_PROJECT_ID`.
- A value provided in the configuration file.

### Authentication

The Meltano Cloud CLI provides `login` and `logout` commands to handle authentication with the Meltano Cloud API.

Upon running the `login` command, the CLI opens the Meltano Cloud login page in a browser. To authenticate, complete the login flow in the browser and then the CLI will store authentication credentials locally in the Meltano Cloud config file. **These credentials should be considered secrets and kept secure**. If Meltano Cloud creates the config file itself, it restricts the permissions such that the OS user has read and write permissions, and no other user has access (aside from the root user). If you manually supply a Meltano Cloud config file, we recommend you take the same precaution.

When running the `logout` command, the CLI makes a request to the Meltano Cloud authentication `logout` API endpoint, which invalidates the locally stored credentials. These invalidated credentials are then deleted from local storage.
