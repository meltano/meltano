# Meltano-common

Meltano-common is a shared module used to develop Extractors and Loaders.

It currently exposes the `meltano` module with the following features:

  - `meltano.job`: Job management (job logging)
  - `meltano.schema`: Schema management
  - `meltano.utils`: Miscellaneous utilites

Issues are tracked at https://gitlab.com/meltano/meltano/issues

# Meltano Fastly extractor

## Configuration

```
FASTLY_API_TOKEN: the API token from Fastly. It should have `Billing` access and `global:read` scope.
```

## Usage

> Note: the `meltano` package will be needed to interact with this package.

```
$ pip install meltano
$ pip install -e .
$ FASTLY_API_TOKEN=<your_api_token> meltano extract fastly | meltano load json
```
