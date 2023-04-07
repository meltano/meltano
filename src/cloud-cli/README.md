# Meltano Cloud CLI

The Meltano Cloud CLI is a a command-line interface for Meltano Cloud, and is (at least until GA) the primary means of interfacing with Meltano Cloud.

The Meltano Cloud CLI can be installed on its own (standalone), or as a module within Meltano.

Regardless of how it is installed, it is provided through the `meltano-cloud` command.

If `meltano` is installed, then it is also exposed through the `meltano cloud` command.

## Installing

[To install for development purposes, refer to the Development section below](#development).

The recommended way to install `meltano` with the pre-GA Cloud features is with the following command:

```sh
pipx install 'git+https://github.com/meltano/meltano.git@cloud'
```

This will create an isolated Python environment with Meltano built from source using `pip`. It will use the `cloud` git branch, which will be the PR target branch for all Cloud-specific features until GA.

The command above installs `meltano` with the Cloud CLI and regular CLI. You can use it to run `meltano` as usually, and also `meltano cloud` (or `meltano-cloud`, which is provided for compatibility with the standalone installation described below).

To _only_ install the Meltano Cloud, the [`subdirectory` argument](https://pip.pypa.io/en/stable/topics/vcs-support/#url-fragments) can be set to `src/cloud-cli`:

```sh
pipx install 'git+https://github.com/meltano/meltano.git@cloud#subdirectory=src/cloud-cli'
```

This only provides the `meltano-cloud` command, which is a lightweight interface for Meltano Cloud. It should be equivalent to running `meltano cloud` with a full Meltano installation.

## Upgrading

For the duration of the `cloud` feature branch, `meltano upgrade` will be disabled. This is because it tries to upgrade using PyPI, which won't have the Meltano Cloud CLI until Meltano Cloud is generally available.

## Development

Typically during development one installs a Python package in editable mode. Poetry does this by default when using `poetry install`, and it can be done with `pip` by using `pip install -e .`.

When a package is installed in editable mode, a [`.pth` file](https://docs.python.org/3/library/site.html) is added to your Python environment's site-packages directory. This file lists directories that are added to Python's `sys.path`, which is the list of paths where Python will look for modules at import-time.

Because this bypasses the construction of the wheel, when Meltano is installed in editable mode it does not have the Cloud CLI package merged into it. To work around this, as symlink at `src/meltano/cloud` points to `../cloud-cli/meltano/cloud`, which makes it appear to Python at import-time as if the packages had been merged.

A symlink would not have worked for building the wheel, as Poetry refuses to follow symlinks during the wheel construction.

This has the added benefit of reserving the path `src/meltano/cloud`, which will prevent conflicts.

## Packaging

To be able to provide the Meltano Cloud CLI as a standalone CLI program with its own dependencies, and as a module within Meltano, an unconventional approach was taken for its packaging.

This approach was required because neither Poetry nor any other mature Python packaging application supports having multiple Python projects located within the same repository with interdependencies.

The Cloud CLI is stored within `src/cloud-cli/`, alongside `src/meltano/`. Within `src/cloud-cli/` are the directories `meltano/cloud/cli`, which makes the Cloud CLI into a [namespace package](https://packaging.python.org/guides/packaging-namespace-packages/). When both packages are installed, their directories are merged, which gives `meltano` a `cloud` and `cloud.cli` module. We currently only use the `cloud.cli` module, but the `cloud` parent module is provided for future use, and organizational cleanliness.

The root `pyproject.toml` contains the following:

```toml
packages = [
  { include = "meltano", from = "src/cloud-cli", format = "wheel" },
  { include = "meltano", from = "src", format = "wheel" },
  { include = "src", format = "sdist" },
  ... # Additional entires omitted
]
```

This instructs Poetry to build an `sdist` (source distribution) containing the entire `src/` directory (with both `meltano/` and `cloud-cli/`), and instructs any [PEP 517 build system](https://pypi.org/project/pep517/) to build a wheel containing the `meltano` directory under `src/` and the `meltano` directory under `src/cloud-cli/` merged together.

The Cloud CLI `pyproject.toml` is typical for a namespace package packaged with Poetry, and warrants no additional explanation here.

## Dependencies

When the root project (`meltano`) is installed, the Cloud CLI source tree is merged into it, and the Cloud CLI dependencies are ignored. Because of this, we must ensure the dependencies of the root project include every dependency used by subprojects like the Cloud CLI. This is automatically enforced by `pre-commit` using the `check-subproject-deps` hook.

## Versioning

For simplicity as much as any other reason, the Cloud CLI uses the same version as Meltano. Its version (found in its `pyproject.toml` file) is bumped by the same tool that bumps Meltano's version elsewhere.

## Linting

As with the rest of Meltano, linting is performed by `pre-commit` using the config predominately located within the root `pyproject.toml`. Per-subproject linting configs are neither supported nor particularly desirable.

## Testing

As with Meltano, tests should be run using `nox`. Nox will take care of `cd`-ing into `src/cloud-cli/`, installing the Cloud CLI standalone into a clean environment, and running its tests (located at `src/cloud-cli/tests/`) using `pytest`.

Separate tests run against the standalone mode of the Cloud CLI are recommended over tests against the non-standalone mode because anything that works in standalone mode will (read: should) work in the non-standalone mode, but the converse is not true.

Tests located under `tests/` may also run tests using `meltano cloud`, as it will always be installed as part of `meltano` (when building from the `cloud` feature branch before GA, and generally afterwards).
