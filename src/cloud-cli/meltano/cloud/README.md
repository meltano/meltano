# Meltano Cloud CLI

`meltano-cloud` is a standalone CLI tool for interacting with the Meltano Cloud API.

## Configuration

`meltano-cloud` can be configured via
`meltano-cloud config set <setting name> <setting value>`.

### Configuration File

Meltano Cloud configuration settings and credentials are stored in a JSON file.
`meltano-cloud` searches for this configuration file using [platformdirs](https://github.com/platformdirs/platformdirs).

If a configuration file is found but the configuration it contains
is invalid, `meltano-cloud` will raise an error rather than continuing its search.

### Settings

The following settings are configurable:

#### `auth_callback_port`

As part of authentication, `meltano-cloud` runs a lightweight, short-lived HTTP
server on `localhost` to handle authentication callbacks. By default, this
server runs on port 9999 but can be configured to another port using this setting.

- Command line flag: `--auth-callback-port`
- Environment variable: `MELTANO_CLOUD_AUTH_CALLBACK_PORT`

#### `base_url`

This is the base URL used for API calls to Meltano Cloud, `https://api.meltano.cloud`
by default.

- Command line flag: `--base-url`
- Environment variable: `MELTANO_CLOUD_BASE_URL`

#### `base_auth_url`

This is the base URL used for authentication calls to Meltano Cloud,
`https://auth.meltano.cloud` by default.

- Command line flag: `--base-auth-url`
- Environment variable: `MELTANO_CLOUD_BASE_AUTH_URL`

#### `organization_id`

This is the default ID for the Meltano Cloud organization to use in interacting with
the Meltano Cloud API.

- Command line flag: `--organization-id`
- Environment variable: `MELTANO_CLOUD_ORGANIZATION_ID`

#### `project_id`

For project-specific commands, this is the project ID to use by default in interacting
with the Meltano Cloud API.

- Command line flag: `--project-id`
- Environment variable: `MELTANO_CLOUD_PROJECT_ID`

### Setting Value Resolution

`meltano-cloud` resolves configuration setting values as follows:

- Use a value provided in a command-line flag, for example
  `meltano-cloud --project-id <project_id> <subcommand>`.
- Use a value provided in an environment variable, for example `MELTANO_CLOUD_PROJECT_ID`.
- Use the value provided in the configuration file.

### Authentication

`meltano-cloud` provides `login` and `logout` commands to handle authentication with
the Meltano Cloud API.

Upon running `meltano-cloud login`, `meltano-cloud` opens the
Cloud login page in a browser. To authenticate, complete the login flow in the browser
and then `meltano-cloud` will store authentication credentials locally in a
`.meltano-cloud` directory in the user's home directory. **These credentials should
be considered secrets and kept secure.**

When running `meltano-cloud logout`, `meltano-cloud` makes a request to the Cloud
auth API's `logout` endpoint, which invalidates the locally stored credentials.
These invalidated credentials are then deleted from local storage.
