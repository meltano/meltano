# Contributing to the Meltano Cloud CLI

General guidelines for contributing to the Meltano Cloud CLI are the same as those for [Meltano Core](https://docs.meltano.com/contribute/).

## Implementation Details

At its core, `meltano-cloud` is merely a thin REST client for the Meltano Cloud API. As such, any contributions should avoid duplicating logic that already exists in Meltano Core or which is implemented within the API itself. Ideally, commands should only behave as follows:

- Manage cloud client configuration such as API credentials, organization and
  project IDs, or default behavior.
- Parse command arguments and configuration for use in making one or more API requests.
- Handle any necessary authentication.
- Make one or more API requests.
- Format API responses for output to the CLI or any relevant output files.

As a rule, any behaviors more complex than this belong in Meltano Core or in the Meltano Cloud API itself.
