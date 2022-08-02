"""Pytest fixtures that use `pytest-docker` to provide Docker services."""

from __future__ import annotations

from pathlib import Path

import pytest

from .snowplow import SnowplowMicro, snowplow, snowplow_optional, snowplow_session


# Originally defined by `pytest-docker`. Overridden to provide a custom location.
@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Get the absolute path to the `docker-compose.yml` file used by `pytest-docker`.

    Returns:
        The absolute path to the `docker-compose.yml` file used by `pytest-docker`.
    """
    return str(Path(__file__).parent.resolve() / "docker-compose.yml")
