"""Snowplow Tracker."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from snowplow_tracker import Emitter, Tracker

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService


class SnowplowTracker(Tracker):
    """Meltano Snowplow Tracker."""

    def __init__(self, project: Project, *, request_timeout: int = 2.0, **kwargs: Any):
        """Create a Snowplow Tracker for the Meltano project.

        Args:
            project: The Meltano project.
            request_timeout: The timeout for all the event emitters.
            kwargs: Additional arguments to pass to the parent snowplow Tracker class.
        """
        settings_service = ProjectSettingsService(project)
        endpoints = settings_service.get("snowplow.collector_endpoints")

        emitters: list[Emitter] = []
        for endpoint in endpoints:
            parsed_url = urlparse(endpoint)
            emitters.append(
                Emitter(
                    endpoint=parsed_url.hostname + parsed_url.path,
                    protocol=parsed_url.scheme or "http",
                    port=parsed_url.port,
                    request_timeout=request_timeout,
                )
            )

        super().__init__(emitters=emitters, **kwargs)
