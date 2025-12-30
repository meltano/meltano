"""Fixtures to interact with Snowplow Micro."""

from __future__ import annotations

import logging
import typing as t

import pytest
import urllib3
from urllib3.util.retry import Retry

from meltano.core.project_settings_service import ProjectSettingsService

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from pytest_docker.plugin import Services

logger = logging.getLogger(__name__)  # noqa: TID251


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

    def get(self, endpoint: str) -> t.Any:
        retries = Retry(total=5, backoff_factor=0.5)
        with urllib3.PoolManager(retries=retries) as http:
            return http.request("GET", f"{self.url}/{endpoint}").json()

    def ping(self) -> bool:
        """Ping the Snowplow Micro service."""
        try:
            self.get("all")
        except Exception:  # pragma: no cover  # noqa: BLE001
            return False

        return True

    def all(self) -> dict[str, int]:
        """Get a dict counting the # of good/bad events, and the total # of events."""
        return self.get("all")

    def good(self) -> list[dict[str, t.Any]]:
        """Get a list of good events."""
        return self.get("good")

    def bad(self) -> list[dict[str, t.Any]]:
        """Get a list of bad events (e.g. those which failed schema validation)."""
        return self.get("bad")

    def reset(self) -> None:
        """Delete all data stored by Snowplow Micro."""
        self.get("reset")


@pytest.fixture(scope="session")
def snowplow_session(
    request: pytest.FixtureRequest,
) -> Generator[SnowplowMicro | None, None, None]:
    """Start a Snowplow Micro Docker container, then yield a `SnowplowMicro` instance.

    The environment variable `$MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS` is set to
    a list containing only the collector endpoint exposed by Snowplow Micro in
    Docker.

    Yields:
        A `SnowplowMicro` instance which will collect events fired within
        tests, and can be queried to obtain info about the fired events, or
        `None` if the creation of a `SnowplowMicro` instance failed.
    """
    try:
        # Getting the `docker_services` fixture essentially causes
        # `docker-compose up` to be run
        services: Services = request.getfixturevalue("docker_services")
        docker_ip: str = request.getfixturevalue("docker_ip")
        port = services.port_for("snowplow", 9090)
        collector_endpoint = f"http://{docker_ip}:{port}"

        client = SnowplowMicro(collector_endpoint)
        services.wait_until_responsive(
            timeout=30,
            pause=0.1,
            check=client.ping,
        )
        yield SnowplowMicro(collector_endpoint)
    except Exception:  # pragma: no cover
        logger.exception("Failed to start Snowplow Micro")
        yield None


@pytest.fixture
def snowplow_optional(
    snowplow_session: SnowplowMicro | None,
    monkeypatch,
) -> Generator[SnowplowMicro | None, None, None]:
    """Provide a clean `SnowplowMicro` instance.

    This fixture resets the `SnowplowMicro` instance, and enables the
    `send_anonymous_usage_stats` setting.

    Yields:
        A freshly reset `SnowplowMicro` instance, or `None` if it could not be created.
    """
    if snowplow_session is None:  # pragma: no cover
        yield None
        return

    if isinstance(ProjectSettingsService.config_override, dict):  # pragma: no branch
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

    Returns:
        A freshly reset `SnowplowMicro` instance.
    """
    if snowplow_optional is None:  # pragma: no cover
        pytest.skip("Unable to start Snowplow Micro")
    return snowplow_optional
