"""Nox configuration."""

from __future__ import annotations

import sys
from pathlib import Path
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
    session.install(".")
    session.install(
        "coverage[toml]",
        "freezegun",
        "mock",
        "pytest",
        "pytest-asyncio",
        "pytest-docker",
        "requests-mock",
    )

    try:
        session.run(
            "coverage",
            "run",
            "--parallel",
            "-m",
            "pytest",
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
