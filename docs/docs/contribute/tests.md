---
title: Tests
description: Meltano is open source software built by a growing team and a community of contributors.
layout: doc
sidebar_position: 10
sidebar_class_name: hidden
---

## Unit Tests

Meltano uses [Pytest](https://docs.pytest.org/) as our primary test framework for Python. You can run the tests after [installing the Meltano Python package](/getting-started/installation#install-meltano) by running the command `pytest` from the root of the repository.

We recommend you familiarize yourself with [Pytest fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html), [Pytest parametrization](https://docs.pytest.org/en/latest/how-to/parametrize.html), and [`unittest.mock`](https://docs.python.org/dev/library/unittest.mock.html).

### Running Pytest

To run Pytest, you can use the following command:

```bash
nox -rs pytest -p 3.11
```

Or, if you want to run a specific test file, for example:

```bash
nox -rs pytest -p 3.11 -- tests/meltano/core/test_task_sets.py
```

### Pytest Best Practices

When possible, ensure Pytest is reporting no errors, failures, warnings, xpasses (i.e. tests that we expected would fail passing instead), or unexpected skips. Additionally, the execution time should be consistent and short. Consider gating a test behind an optional `slow` or similar Pytest marker if it is slow or resource-hungry.

After running Pytest in CI, a table summarizing all of the runs for every supported platform can be viewed by going to `https://github.com/meltano/meltano/actions/workflows/test.yml?query=branch:<your-branch-name>`, and selecting the top (i.e. most recent) result.

If a test needs a particular environment in which to execute, do not rely on other tests to establish it. Tests that need a particular environment should either explicitly depend on other tests (via a Pytest plugin), use a fixture to establish it, or establish it themselves. It should be possible to execute the tests in a random order, and have them all (or any subset of them) consistently pass.

### Using Docker under Pytest

If you'd like to add tests that rely on a Docker container running, you can do that by using `pytest-docker`. A session-scoped fixture for the service running under Docker should be added within the directory `tests/fixtures/docker`. The Docker service itself should be defined in `tests/fixtures/docker/docker-compose.yml`.

Take care to ensure that if `docker compose` is not available, tests that rely on it are skipped, as we cannot rely on it being present, but that is not sufficient reason to have those tests fail. Refer to how the fixtures currently implemented in `tests/fixtures/docker` handle this for guidance.

## Integration Tests

Meltano use a small homegrown framework:q! for integration tests that are generated from the markdown guides in our example library and managed via [Github Workflows](https://docs.github.com/en/actions/workflows/):

- [`docs/example-library/<test-name>`](https://github.com/meltano/meltano/tree/main/docs/example-library) holds the markdown guide and the meltano YAML files. The test script is created from the markdown guide via [mdsh](https://github.com/bashup/mdsh),
  and the YAML files are used during test validation.
- - `.github/workflows/integration_tests.yml` is the workflow definition that actually controls the execution of the tests. In order for an example guide to actually be treated as an integration test, it must be added to test matrix in [integration_tests.yml](https://github.com/meltano/meltano/tree/main/.github/workflows) workflow.
- [`integration/validate.sh`](https://github.com/meltano/meltano/tree/main/integration/validate.sh) is the main entry point for all integration tests. It takes care of producing the script from the markdown, injecting a logging YAML, diffing the meltano yaml's, and calling the additional per-test validations when required.
- `integration/<test-name>/validate.sh` - optional additional tests to run for a test. Often, this won't even be needed, but the ability is available if you want to run extended checks (i.e. grepping logs, running sql, etc)

### Example library entry

For example if you wanted to test and document how to transition from using `elt` to `run` you might create an entry like
the bellow in `docs/example-library/transition-from-elt-to-run/index.md`:

````markdown
# Example of how to transition from `meltano elt` to `meltano run`

This example shows how to transition an `el` or `elt` task with a custom state-id to a `job` executed via `run`.
To follow along with this example, download link to meltano yml to a fresh project and run:

```
meltano install
```

Then assuming you had an `el` job invoked like so:

```shell
meltano el --state-id=my-custom-id tap-gitlab target-postgres
```

You would first need to rename the id to match meltano's internal pattern:

```shell
meltano state copy my-custom-id tap-gitlab-to-target-postgres
```

Then you can create a job and execute it using `meltano run`:


```shell
meltano job add my-new-job --task="tap-gitlab target-postgres"
meltano run my-new-job
```
````

Our integration framework will then parse this markdown, searching for code fences marked as `shell` and generate orchestration script for you that looks something like:

```shell
meltano install
meltano el --state-id=my-custom-id tap-gitlab target-postgres
meltano state copy my-custom-id tap-gitlab-to-target-postgres
meltano job add my-new-job --task="tap-gitlab target-postgres"
meltano run my-new-job
```

Every example should also include:

1. a `meltano.yml` that users can start with.
2. a `ending-meltano.yml` that covers what the meltano.yml should look like after having run through the guide.

These two are required for examples that will be used as integration tests. The `meltano.yml` will be used at the start
of the test when starting the orchestration script. At the end of the test's the resulting `meltano.yml` yielded by the orchestration script will be diffed against the `ending-meltano.yml` and will need to match!

### Validating a new example library entry

To actually have the `docs/example-library/transition-from-elt-to-run/` guide created above tested, it must be added to test matrix in [integration_tests.yml](https://github.com/meltano/meltano/tree/main/.github/workflows) workflow.

## meltano yaml jsonschema validations

To validate the meltano.yml jsonschema the workflow [`.github/workflows/check_jsonschema.yml`](https://github.com/meltano/meltano/blob/main/.github/workflows/check_jsonschema.yml) is used. It runs [check_jsonschema](https://github.com/python-jsonschema/check-jsonschema) on the various meltano.yml files shipped in the example library.
