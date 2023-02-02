"""Nox configuration.

- Run `nox -l` to list the sessions Nox can run.
- Run `nox -t lint` to run linting.
- Run `nox -t test` to run tests.
- Run `nox` to run all sessions.
- Run `nox -s <session name>` to run a particular session.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from random import randint

from nox import Session

try:
    from nox_poetry import session as nox_session
except ImportError:
    raise SystemExit(
        "Nox failed to import the 'nox-poetry' package. Please install it "
        f"using the following command: {sys.executable} -m pip install nox-poetry"
    ) from None

# NOTE: The module docstring above is printed when `nox -l` is run.

# Dependencies for tests and type checking are defined in `pyproject.toml`, and
# locked in `poetry.lock`. The various Nox sessions defined here install the
# subset of them they require.

# We use `nox-poetry` to ensure the version installed is consistent with
# `poetry.lock`. The single source of truth for our Python test and type checking
# dependencies is `pyproject.toml`. Other linting and checks are performed by
# `pre-commit`, where each check specifies its own dependencies. There should be
# no duplicated dependencies between `pyproject.toml` and
# `.pre-commit-config.yaml`.

root_path = Path(__file__).parent
python_versions = ("3.7", "3.8", "3.9", "3.10", "3.11")
main_python_version = "3.10"
pytest_deps = (
    "colorama",  # colored output in Windows
    "freezegun",
    "mock",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-docker",
    "pytest-order",
    "pytest-randomly",
    "pytest-xdist",
    "requests-mock",
)


def _run_pytest(session: Session) -> None:
    try:
        session.env.update(
            {
                "COVERAGE_RCFILE": str(root_path / "pyproject.toml"),
                "COVERAGE_FILE": str(root_path / f".coverage.{session.name}"),
            }
        )
        session.run(
            "pytest",
            "--cov=meltano",
            "--cov=tests",
            "tests/",
            f"--randomly-seed={randint(0, 2**32 - 1)}",  # noqa: S311, WPS432
            *session.posargs,
        )
    finally:
        session.notify("coverage", posargs=[])


@nox_session(
    name="pytest-cloud-cli",
    python=python_versions,
    tags=("test", "pytest"),
)
def pytest_cloud_cli(session: Session) -> None:
    """Run pytest to test the Meltano Cloud CLI.

    Args:
        session: Nox session.
    """
    session.install("src/cloud-cli", *pytest_deps)

    with session.chdir("src/cloud-cli"):
        _run_pytest(session)


@nox_session(
    name="pytest-meltano",
    python=python_versions,
    tags=("test", "pytest"),
)
def pytest_meltano(session: Session) -> None:
    """Run pytest to test Meltano.

    Args:
        session: Nox session.
    """
    backend_db = os.environ.get("PYTEST_BACKEND", "sqlite")
    session.install(
        ".[mssql,azure,gcs,s3]" if backend_db == "mssql" else ".[azure,gcs,s3]",
        *pytest_deps,
    )
    _run_pytest(session)


@nox_session(python=main_python_version)
def coverage(session: Session) -> None:
    """Combine and report previously generated coverage data.

    Args:
        session: Nox session.
    """
    args = session.posargs or ("report",)

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        # Coverage does not combine properly if `$COVERAGE_FILE` is set, so we
        # remove it from the env, then move the default `.coverage` file to
        # wherever `$COVERAGE_FILE` says it should go.
        coverage_file = session.env.pop("COVERAGE_FILE", ".coverage")
        session.run("coverage", "combine")
        shutil.move(".coverage", coverage_file)
        session.env["COVERAGE_FILE"] = coverage_file

    session.run("coverage", *args)


@nox_session(
    name="pre-commit",
    python=main_python_version,
    tags=("lint",),
)
def pre_commit(session: Session) -> None:
    """Run pre-commit linting and auto-fixes.

    Args:
        session: Nox session.
    """
    args = session.posargs or ("run", "--all-files")
    session.install("pre-commit")
    session.run("pre-commit", *args)


@nox_session(
    python=main_python_version,
    tags=("lint",),
)
def mypy(session: Session) -> None:
    """Run mypy type checking.

    Args:
        session: Nox session.
    """
    session.install(
        ".",
        "mypy",
        "sqlalchemy2-stubs",
        "types-croniter",
        "types-jsonschema",
        "types-psutil",
        "types-PyYAML",
        "types-requests",
        "boto3-stubs[essential]",
    )
    session.run("mypy", *session.posargs)
