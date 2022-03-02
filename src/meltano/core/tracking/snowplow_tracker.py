"""Snowplow Tracker."""

from __future__ import annotations

from urllib.parse import urlparse

from snowplow_tracker import Emitter, Subject, Tracker

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService


def get_snowplow_tracker(
    project: Project,
    user_id: str | None = None,
    request_timeout: int | None = None,
) -> Tracker:
    """Get a Snowplow Tracker instance.

    Args:
        project: The Meltano project to get the tracker for.
        user_id: User ID.
        request_timeout: Request timeout.

    Returns:
        Snowplow Tracker instance.
    """
    settings_service = ProjectSettingsService(project)
    endpoints = settings_service.get("snowplow.collector_endpoints")

    emitters: list[Emitter] = []
    subject = Subject()

    if user_id:
        subject.set_user_id(user_id)

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

    return Tracker(emitters=emitters, subject=subject)
