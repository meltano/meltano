"""Fixtures to interact with Snowplow Micro."""

from __future__ import annotations

import os
import subprocess
from contextlib import contextmanager
from typing import Any

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from meltano.core.project_settings_service import ProjectSettingsService


@contextmanager
def env(**environment) -> None:
    """Temporarily update environment variables."""
    original = dict(os.environ)
    os.environ.update(environment)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


class SnowplowMicro:
    """Wrapper around the Snowplow Micro REST API."""

    def __init__(self, collector_endpoint: str):
        """Initialize the `SnowplowMicro` instance.

        Parameters:
            collector_endpoint: The HTTP URL to the Snowplow Micro service.
        """
        self.collector_endpoint = collector_endpoint
        self.url = f"{collector_endpoint}/micro"
        self.session = requests.Session()
        self.session.mount(
            "http://", HTTPAdapter(max_retries=Retry(connect=5, backoff_factor=0.5))
        )
        self.all()  # Wait until a connection is established

    def all(self) -> dict[str, int]:
        """Get a dict counting the number of good/bad events, and the total number of events."""
        return self.session.get(f"{self.url}/all").json()

    def good(self) -> list[dict[str, Any]]:
        """Get a list of good events."""
        return self.session.get(f"{self.url}/good").json()

    def bad(self) -> list[dict[str, Any]]:
        """Get a list of bad events (e.g. those which failed schema validation)."""
        return self.session.get(f"{self.url}/bad").json()

    def reset(self) -> None:
        """Delete all data stored by Snowplow Micro."""
        self.session.get(f"{self.url}/reset")


@pytest.fixture(scope="session")
def snowplow_session(request) -> SnowplowMicro | None:
    """Start a Snowplow Micro Docker container, then yield a `SnowplowMicro` instance for it.

    The environment variable `$MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS` is set to a list containing
    only the collector endpoint exposed by Snowplow Micro in Docker.

    Yields:
        A `SnowplowMicro` instance which will collect events fired within tests, and can be queried
        to obtain info about the fired events, or `None` if the creation of a `SnowplowMicro`
        instance failed.
    """
    try:
        # Getting the `docker_services` fixture essentially causes `docker-compose up` to be run
        request.getfixturevalue("docker_services")
    except Exception:
        yield None
    else:
        args = ("docker", "port", f"pytest{os.getpid()}_snowplow_1")
        proc = subprocess.run(args, capture_output=True, text=True)
        address_and_port = proc.stdout.strip().split(" -> ")[1]
        collector_endpoint = f"http://{address_and_port}"
        try:  # noqa: WPS505
            yield SnowplowMicro(collector_endpoint)
        except Exception:
            yield None


@pytest.fixture()
def snowplow_optional(snowplow_session: SnowplowMicro | None) -> SnowplowMicro | None:
    """Provide a clean `SnowplowMicro` instance.

    This fixture resets the `SnowplowMicro` instance, and enables the
    `send_anonymous_usage_stats` setting.

    Yields:
        A freshly reset `SnowplowMicro` instance, or `None` if it could not be created.
    """
    snowplow_session.reset()

    if isinstance(ProjectSettingsService.config_override, dict):
        original_config_override = ProjectSettingsService.config_override.copy()
        ProjectSettingsService.config_override.pop(
            "send_anonymous_usage_stats", None
        )
    else:
        original_config_override = ProjectSettingsService.config_override

    with env(
        MELTANO_SEND_ANONYMOUS_USAGE_STATS="True",
        MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS=f'["{snowplow_session.collector_endpoint}"]',
    ):
        try:
            yield snowplow_session
        finally:
            ProjectSettingsService.config_override = original_config_override
            snowplow_session.reset()


@pytest.fixture()
def snowplow(snowplow_optional: SnowplowMicro | None) -> SnowplowMicro:
    """Provide a clean `SnowplowMicro` instance.

    This fixture resets the `SnowplowMicro` instance, and enables the
    `send_anonymous_usage_stats` setting.

    Returns:
        A freshly reset `SnowplowMicro` instance.
    """
    if snowplow_session is None:
        pytest.skip("Unable to start Snowplow Micro")
    return snowplow_optional
