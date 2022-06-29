---
title: Tests
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
weight: 10
---

Meltano uses [Pytest](https://docs.pytest.org/) as our primary test framework for Python. You can run the tests after [installing the Meltano Python package](/guide/installation#install-meltano) by running the command `pytest` from the root of the repository.

We recommend you familiarize yourself with [Pytest fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html), [Pytest parametrization](https://docs.pytest.org/en/latest/how-to/parametrize.html), and [`unittest.mock`](https://docs.python.org/dev/library/unittest.mock.html).

### Using Docker under Pytest

If you'd like to add tests that rely on a Docker container running, you can do that by using `pytest-docker`. A session-scoped fixture for the service running under Docker should be added within the directory `tests/fixtures/docker`. The Docker service itself should be defined in `tests/fixtures/docker/docker-compose.yml`.

Take care to ensure that if `docker-compose` is not available, tests that rely on it are skipped, as we cannot rely on it being present, but that is not sufficient reason to have those tests fail. Refer to how the fixtures currently implemented in `tests/fixtures/docker` handle this for guidance.
