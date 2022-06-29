---
title: Tests
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

## Unit Tests

Meltano uses [Pytest](https://docs.pytest.org/) as our primary test framework for Python. You can run the tests after [installing the Meltano Python package](/guide/installation#install-meltano) by running the command `pytest` from the root of the repository.

We recommend you familiarize yourself with [Pytest fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html), [Pytest parametrization](https://docs.pytest.org/en/latest/how-to/parametrize.html), and [`unittest.mock`](https://docs.python.org/dev/library/unittest.mock.html).

### Using Docker under Pytest

If you'd like to add tests that rely on a Docker container running, you can do that by using `pytest-docker`. A session-scoped fixture for the service running under Docker should be added within the directory `tests/fixtures/docker`. The Docker service itself should be defined in `tests/fixtures/docker/docker-compose.yml`.

Take care to ensure that if `docker-compose` is not available, tests that rely on it are skipped, as we cannot rely on it being present, but that is not sufficient reason to have those tests fail. Refer to how the fixtures currently implemented in `tests/fixtures/docker` handle this for guidance.

## Integration Tests

Meltano use a small homegrown framework for integration tests that are generated from the markdown guides in our example library and managed via [Github Workflows](https://docs.github.com/en/actions/workflows/):

- [`docs/example-library/<test-name>`](https://github.com/meltano/meltano/tree/main/docs/example-library) holds the markdown guide and the meltano YAML files. The test script is created from the markdown guide via [mdsh](https://github.com/bashup/mdsh),
and the YAML files are used during test validation.
- - `.github/workflows/integration_tests.yml` is the workflow definition that actually controls the execution of the tests. In order for an example guide to actually be treated as an integration test, it must be added to test matrix in [integration_tests.yml](https://github.com/meltano/meltano/tree/main/.github/workflows) workflow.
- [`integration/validate.sh`](https://github.com/meltano/meltano/tree/main/integration/validate.sh) is the main entry point for all integration tests. It takes care of producing the script from the markdown, injecting a logging YAML, diffing the meltano yaml's, and calling the additional per-test validations when required.
- `integration/<test-name>/validate.sh` - optional additional tests to run for a test. Often, this won't even be needed, but the ability is available if you want to run extended checks (i.e. grepping logs, running sql, etc)

## meltano yaml jsonschema validations

To validate the meltano.yml jsonschema the workflow [`.github/workflows/check_jsonschema.yml`](https://github.com/meltano/meltano/blob/main/.github/workflows/check_jsonschema.yml) is used. It runs [check_jsonschema](https://github.com/python-jsonschema/check-jsonschema) on the various meltano.yml files shipped in the example library.
