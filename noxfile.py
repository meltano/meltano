#!/usr/bin/env -S uv run --script

# /// script
# dependencies = ["nox"]
# ///

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
nox.options.reuse_venv = "yes"

root_path = Path(__file__).parent
pyproject = nox.project.load_toml()
python_versions = nox.project.python_versions(pyproject)

main_python_version = Path(".python-version").read_text().strip()


def _uv_sync(session: nox.Session, *args: str) -> None:
    env = {
        "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
        "UV_NO_CONFIG": "1",
    }
    session.run_install("uv", "--quiet", "pip", "uninstall", "uv", env=env)
    session.run_install(
        "uv",
        "--quiet",
        "sync",
        "--locked",
        "--no-dev",
        f"--python={session.virtualenv.location}",
        *args,
        env=env,
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
                "UV_NO_CONFIG": "1",
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
        extras.append("postgres")
    elif backend_db == "postgresql_psycopg2":
        extras.append("psycopg2")

    _uv_sync(session, "--group=testing", *(f"--extra={extra}" for extra in extras))
    _run_pytest(session)


@nox.session(
    name="pytest-lowest-requirements",
    tags=("test", "pytest"),
    python=python_versions[0],
)
def pytest_lowest_requirements(session: nox.Session) -> None:
    """Test with lowest requirements."""
    backend_db = os.environ.get("PYTEST_BACKEND", "sqlite")
    extras = ["azure", "gcs", "s3", "containers"]

    if backend_db == "mssql":
        extras.append("mssql")
    elif backend_db == "postgresql":
        extras.append("postgres")
    elif backend_db == "postgresql_psycopg2":
        extras.append("psycopg2")

    _uv_sync(session, "--group=testing", *(f"--extra={extra}" for extra in extras))

    tmpdir = Path(session.create_tmp())
    tmpfile = tmpdir / "requirements.txt"
    tmpfile.unlink(missing_ok=True)

    env = {
        "UV_PROJECT_ENVIRONMENT": session.virtualenv.location,
        "UV_NO_CONFIG": "1",
    }
    session.run_install(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        f"--python={session.python}",
        "--group=testing",
        *(f"--extra={extra}" for extra in extras),
        "--universal",
        "--resolution=lowest-direct",
        f"-o={tmpfile.as_posix()}",
        env=env,
    )
    session.install("-r", f"{tmpdir}/requirements.txt", env=env)
    _run_pytest(session)


@nox.session(python=main_python_version, default=False)
def coverage(session: nox.Session) -> None:
    """Combine and report previously generated coverage data.

    Args:
        session: Nox session.
    """
    args = session.posargs or ("report",)

    _uv_sync(session, "--group=coverage")

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
    _uv_sync(session, "--group=pre-commit")
    session.run("pre-commit", *args)


@nox.session(
    python=main_python_version,
    tags=("lint",),
)
def typing(session: nox.Session) -> None:
    """Run mypy and ty type checking.

    Args:
        session: Nox session.
    """
    _uv_sync(session, "--group=typing", "--all-extras")
    output_format = "github" if os.getenv("GITHUB_ACTIONS") == "true" else "concise"
    session.run("ty", "check", f"--output-format={output_format}", *session.posargs)
    session.run("mypy", *session.posargs)


if __name__ == "__main__":
    nox.main()
