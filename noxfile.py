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
python_versions = ["3.11", "3.10", "3.9", "3.8", "3.7"]
main_python_version = "3.9"
locations = "src", "noxfile.py"


@nox_session(python=python_versions)
def tests(session: Session) -> None:
    """Execute pytest tests and compute coverage.

    Args:
        session: Nox session.
    """
    session.cd("src/meltano")

    backend_db = os.environ.get("PYTEST_BACKEND", "sqlite")

    if backend_db == "mssql":
        session.install(".[mssql,azure,gcs,s3]")

    else:
        session.install(".[azure,gcs,s3]")

    session.install(
        "colorama==0.4.6",  # colored output in Windows
        "freezegun==1.2.2",
        "mock==5.0.1",
        "pytest==7.2.1",
        "pytest-asyncio==0.20.3",
        "pytest-cov==4.0.0",
        "pytest-docker==1.0.1",
        "pytest-order==1.0.1",
        "pytest-randomly==3.12.0",
        "pytest-xdist==3.1.0",
        "requests-mock==1.10.0",
        # Used by pytest-xdist to aid with handling resource intensive processes.
        "setproctitle==1.3.2",
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
    session.cd("src/meltano")

    args = session.posargs or ["report"]

    session.install(
        "coverage[toml]==7.1.0",
    )

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", *args)


@nox_session(python=main_python_version)
def mypy(session: Session) -> None:
    """Run mypy type checking.

    Args:
        session: Nox session.
    """
    session.cd("src/meltano")

    args = session.posargs or [
        "meltano/",
        "--exclude",
        "meltano/migrations/",
    ]

    session.install(".")
    session.install(
        "boto3-stubs[essential]==1.26.58",
        "mypy==0.960",
        "sqlalchemy2-stubs==0.0.2a32",
        "types-croniter==1.3.2",
        "types-psutil==5.9.5.5",
        "types-requests==2.28.9",
    )
    session.run("mypy", *args)
