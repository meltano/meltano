"""Nox configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from random import randint
from textwrap import dedent

try:
    from nox_poetry import Session
    from nox_poetry import session as nox_session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.
    Please install it using the following command:
    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None


package = "meltano"
python_versions = ["3.10", "3.9", "3.8", "3.7"]
main_python_version = "3.9"
locations = "src", "tests", "noxfile.py"


@nox_session(python=python_versions)
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage.

    Args:
        session: Nox session.
    """
    backend_db = os.environ.get("PYTEST_BACKEND", "sqlite")

    if backend_db == "mssql":
        session.install(".[mssql,azure,gcs,s3]")

    else:
        session.install(".[azure,gcs,s3]")

    session.install(
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

    try:
        session.run(
            "pytest",
            f"--randomly-seed={randint(0, 2**32-1)}",  # noqa: S311, WPS432
            *session.posargs,
            env={"NOX_CURRENT_SESSION": "tests"},
        )
    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox_session(python=main_python_version)
def coverage(session: Session) -> None:
    """Upload coverage data.

    Args:
        session: Nox session.
    """
    args = session.posargs or ["report"]

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox_session(python=main_python_version)
def mypy(session: Session) -> None:
    """Run mypy type checking.

    Args:
        session: Nox session.
    """
    args = session.posargs or ["src/meltano", "--exclude", "src/meltano/migrations/"]

    session.install(".")
    session.install(
        "mypy",
        "sqlalchemy2-stubs",
        "types-croniter",
        "types-requests",
        "boto3-stubs[essential]",
    )
    session.run("mypy", *args)
