"""Nox configuration.

- Run `nox -l` to list the sessions Nox can run.
- Run `nox -t lint` to run linting.
- Run `nox -t test` to run tests.
- Run `nox` to run all sessions.
- Run `nox -s <session name>` to run a particular session.
"""

from __future__ import annotations

import os
from pathlib import Path
from random import randint

import nox

# NOTE: The module docstring above is printed when `nox -l` is run.

# Dependencies for tests and type checking are defined in `pyproject.toml`,
# locked in `uv.lock`.
# The various Nox sessions defined here install the subset of them they require.

# The single source of truth for our Python test and type checking
# dependencies is `pyproject.toml`. Other linting and checks are performed by
# `pre-commit`, where each check specifies its own dependencies. There should be
# no duplicated dependencies between `pyproject.toml` and
# `.pre-commit-config.yaml`.

nox.needs_version = ">=2025.2.9"
nox.options.default_venv_backend = "uv"
nox.options.sessions = [
    "mypy",
    "pre-commit",
    "pytest",
]

root_path = Path(__file__).parent
pyproject = nox.project.load_toml()
python_versions = nox.project.python_versions(pyproject)

main_python_version = "3.13"

UV_SYNC_COMMAND = (
    "uv",
    "sync",
    "--locked",
    "--no-dev",
)


def _run_pytest(session: nox.Session) -> None:
    random_seed = randint(0, 2**32 - 1)  # noqa: S311
    args = session.posargs or ("tests/",)
    try:
        session.env.update(
            {
                "COVERAGE_RCFILE": str(root_path / "pyproject.toml"),
                "COVERAGE_FILE": str(
                    root_path / f".coverage.{random_seed:010}.{session.name}",
                ),
                "NOX_CURRENT_SESSION": "tests",
            },
        )

        session.run(
            "coverage",
            "run",
            "-m",
            "pytest",
            "--durations=10",
            "--order-scope=module",
            "--timeout=300",
            "-n=auto",
            "--dist=loadfile",
            f"--randomly-seed={random_seed}",
            *args,
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(
    name="pytest",
    python=python_versions,
    tags=("test", "pytest"),
)
def pytest_meltano(session: nox.Session) -> None:
    """Run pytest to test Meltano.

    Args:
        session: Nox session.
    """
    backend_db = os.environ.get("PYTEST_BACKEND", "sqlite")
    extras = ["azure", "gcs", "s3", "containers"]

    if backend_db == "mssql":
        extras.append("mssql")
    elif backend_db == "postgresql":
        extras.append("psycopg2")
    elif backend_db == "postgresql_psycopg3":
        extras.append("postgres")

    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=testing",
        *(f"--extra={extra}" for extra in extras),
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    _run_pytest(session)


@nox.session(python=main_python_version)
def coverage(session: nox.Session) -> None:
    """Combine and report previously generated coverage data.

    Args:
        session: Nox session.
    """
    args = session.posargs or ("report",)

    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=coverage",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox.session(
    name="pre-commit",
    python=main_python_version,
    tags=("lint",),
)
def pre_commit(session: nox.Session) -> None:
    """Run pre-commit linting and auto-fixes.

    Args:
        session: Nox session.
    """
    args = session.posargs or ("run", "--all-files")
    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=pre-commit",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pre-commit", *args)


@nox.session(
    python=main_python_version,
    tags=("lint",),
)
def mypy(session: nox.Session) -> None:
    """Run mypy type checking.

    Args:
        session: Nox session.
    """
    session.run_install(
        *UV_SYNC_COMMAND,
        "--group=typing",
        "--extra=mssql",
        "--extra=azure",
        "--extra=gcs",
        "--extra=s3",
        "--extra=containers",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("mypy", *session.posargs)
