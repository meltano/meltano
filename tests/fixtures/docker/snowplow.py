"""Fixtures to interact with Snowplow Micro."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any
from urllib.request import urlopen

import backoff
import pytest

from meltano.core.project_settings_service import ProjectSettingsService


class SnowplowMicro:
    """Wrapper around the Snowplow Micro REST API."""

    def __init__(self, collector_endpoint: str):
        """Initialize the `SnowplowMicro` instance.

        Args:
            collector_endpoint: The HTTP URL to the Snowplow Micro service.
        """
        self.collector_endpoint = collector_endpoint
        self.url = f"{collector_endpoint}/micro"
        self.all()  # Wait until a connection is established

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=5)
    def get(self, endpoint: str) -> Any:
        with urlopen(f"{self.url}/{endpoint}") as response:
            return json.load(response)

    def all(self) -> dict[str, int]:
        """Get a dict counting the number of good/bad events, and the total number of events."""
        return self.get("all")

    def good(self) -> list[dict[str, Any]]:
        """Get a list of good events."""
        return self.get("good")

    def bad(self) -> list[dict[str, Any]]:
        """Get a list of bad events (e.g. those which failed schema validation)."""
        return self.get("bad")

    def reset(self) -> None:
        """Delete all data stored by Snowplow Micro."""
        self.get("reset")


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
        args = ("docker", "port", f"pytest{os.getpid()}_snowplow_1")
        proc = subprocess.run(args, capture_output=True, text=True)
        address_and_port = proc.stdout.strip().split(" -> ")[1]
        collector_endpoint = f"http://{address_and_port}"
        yield SnowplowMicro(collector_endpoint)
    except Exception:  # pragma: no cover
        yield None


@pytest.fixture
def snowplow_optional(
    snowplow_session: SnowplowMicro | None, monkeypatch
) -> SnowplowMicro | None:
    """Provide a clean `SnowplowMicro` instance.

    This fixture resets the `SnowplowMicro` instance, and enables the
    `send_anonymous_usage_stats` setting.

    Yields:
        A freshly reset `SnowplowMicro` instance, or `None` if it could not be created.
    """
    if snowplow_session is None:  # pragma: no cover
        yield None
    else:
        if isinstance(ProjectSettingsService.config_override, dict):
            monkeypatch.delitem(
                ProjectSettingsService.config_override,
                "send_anonymous_usage_stats",
                raising=False,
            )
        monkeypatch.setenv("MELTANO_SEND_ANONYMOUS_USAGE_STATS", "True")
        monkeypatch.setenv(
            "MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS",
            f'["{snowplow_session.collector_endpoint}"]',
        )
        try:
            yield snowplow_session
        finally:
            snowplow_session.reset()


@pytest.fixture
def snowplow(snowplow_optional: SnowplowMicro | None) -> SnowplowMicro:
    """Provide a clean `SnowplowMicro` instance.

    This fixture resets the `SnowplowMicro` instance, and enables the
    `send_anonymous_usage_stats` setting.

    Yields:
        A freshly reset `SnowplowMicro` instance.
    """
    if snowplow_optional is None:  # pragma: no cover
        pytest.skip("Unable to start Snowplow Micro")
    yield snowplow_optional
