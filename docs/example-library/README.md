# Example Library

This directory contains various examples of how to interact with and use the meltano cli.
Within each directory you'll find:

- a `meltano.yml` file that you can download and use as a jumping of point
- a `index.md` file that contains step-by-step instructions for the example
- a `ending-meltano.yml` file that represents what the end state of your meltano yaml should look like

I many cases, these examples actually double as our [integration tests](https://docs.meltano.com/contribute/tests), and so should always be up-to-date and functional with the latest Meltano release.

## Library Index

| Example name                                           | Description                                                                                   |
|--------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| [meltano basics](/docs/example-library/meltano-basics/) | A basic 30 second demo - using a prepopulated meltano.yml.                                    |
| [meltano run](/docs/example-library/meltano-run/)      | How to get up and running using `meltano run` with `tap-gitlab`, `target-postgres` and `dbt`. |

## Contributing to the Meltano example library

If you'd like to contribute to the Meltano example library, please see the [contributing guide](/docs/contributing/contributing.md).
