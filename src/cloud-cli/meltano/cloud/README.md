# Meltano Cloud CLI

`meltano-cloud` is a standalone CLI tool for interacting with the Meltano Cloud API. It is also available as a subcommand of `meltano`, i.e. `meltano cloud`.

## Configuration File

Meltano Cloud configuration settings and credentials are stored in a JSON file. The CLI searches for this configuration file in standard locations using [`platformdirs`](https://github.com/platformdirs/platformdirs).

If a configuration file is found but the configuration it contains is invalid, the CLI will raise an error rather than continuing its search.

## Authentication

The Meltano Cloud CLI provides `login` and `logout` commands to handle authentication with the Meltano Cloud API.

Upon running the `login` command, the CLI opens the Meltano Cloud login page in a browser. To authenticate, complete the login flow in the browser and then the CLI will store authentication credentials locally in the Meltano Cloud config file. **These credentials should be considered secrets and kept secure**. If Meltano Cloud creates the config file itself, it restricts the permissions such that the OS user has read and write permissions, and no other user has access (aside from the root user). If you manually supply a Meltano Cloud config file, we recommend you take the same precaution.

When running the `logout` command, the CLI makes a request to the Meltano Cloud authentication `logout` API endpoint, which invalidates the locally stored credentials. These invalidated credentials are then deleted from local storage.
