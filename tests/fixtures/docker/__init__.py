"""Pytest fixtures that use `pytest-docker` to provide Docker services."""

from __future__ import annotations

import pytest

from meltano.core.utils.compat import importlib_resources

from .snowplow import SnowplowMicro, snowplow, snowplow_optional, snowplow_session

__all__ = [
    "SnowplowMicro",
    "snowplow",
    "snowplow_optional",
    "snowplow_session",
]


# Originally defined by `pytest-docker`. Overridden to provide a custom location.
@pytest.fixture(scope="session")
def docker_compose_file() -> str:
    """Get the absolute path to the `docker-compose.yml` file used by `pytest-docker`.

    Returns:
        The absolute path to the `docker-compose.yml` file used by `pytest-docker`.
    """
    return str(importlib_resources.files(__package__) / "docker-compose.yml")
