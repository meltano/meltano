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
