"""Meltano telemetry."""

from __future__ import annotations

import datetime
import locale
import re
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import tzlocal
from backports.cached_property import cached_property
from snowplow_tracker import Emitter, SelfDescribingJson, Tracker
from structlog.stdlib import get_logger

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.project import ProjectContext
from meltano.core.utils import hash_sha256

from .environment import environment_context
from .legacy_tracker import LegacyTracker

URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

logger = get_logger(__name__)


def check_url(url: str) -> bool:
    """Check if the given URL is valid.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is valid, False otherwise.
    """
    return bool(re.match(URL_REGEX, url))


# TODO: Can we store some of this info to make future invocations faster?
class MeltanoTracker:
    """Meltano Tracker."""

    def __init__(
        self,
        project: Project,
        request_timeout: float | tuple[float, float] | None = None,
    ):
        """Initialize a tracker for the Meltano project.

        Args:
            project: The Meltano project.
            request_timeout: Timeout for the HTTP requests. Can be set either as single float value
                which applies to both `connect` AND `read` timeout, or as tuple with two float
                values which specify the `connect` and `read` timeouts separately.
        """
        self.project = project
        self.settings_service = ProjectSettingsService(project)
        endpoints = self.settings_service.get("snowplow.collector_endpoints")

        emitters: list[Emitter] = []
        for endpoint in endpoints:
            if not check_url(endpoint):
                logger.warning("invalid_snowplow_endpoint", endpoint=endpoint)
                continue
            parsed_url = urlparse(endpoint)
            emitters.append(
                Emitter(
                    endpoint=parsed_url.hostname + parsed_url.path,
                    protocol=parsed_url.scheme or "http",
                    port=parsed_url.port,
                    request_timeout=request_timeout,
                )
            )

        if emitters:
            self.snowplow_tracker = Tracker(
                emitters=emitters, request_timeout=request_timeout
            )
            self.snowplow_tracker.subject.set_lang(locale.getdefaultlocale()[0])
            self.snowplow_tracker.subject.set_timezone(self.timezone_name)
            # No good way to get the IP address without making a web request. We could use UPnP, but
            # that's pretty heavyweight, both in terms of runtime, and required dependencies.
            # self.subject.set_ip_address()
        else:
            self.snowplow_tracker = None

        self.send_anonymous_usage_stats = self.settings_service.get(
            "send_anonymous_usage_stats", True
        )

        self.contexts: tuple[SelfDescribingJson] = (
            environment_context,
            ProjectContext(project),
        )

    @cached_property
    def timezone_name(self) -> str:
        """The local timezone as an IANA TZ database name if possible, or abbreviation otherwise.

        Examples:
            The timezone name as an IANA timezone database name:

                >>> SnowplowTracker(project).timezone_name
                'Europe/Berlin'

            The timezone name as an IANA timezone abbreviation because the full name was not found:

                >>> SnowplowTracker(project).timezone_name
                'CET'
        """
        try:
            return tzlocal.get_localzone_name()
        except Exception:
            return datetime.datetime.now().astimezone().tzname()

    @contextmanager
    def with_contexts(self, *extra_contexts) -> MeltanoTracker:
        """Context manager within which the `MeltanoTracker` has additional Snowplow contexts."""
        prev_contexts = self.contexts
        self.contexts = (*prev_contexts, *extra_contexts)
        try:
            yield self
        finally:
            self.contexts = prev_contexts

    def can_track(self) -> bool:
        return self.snowplow_tracker is not None and self.send_anonymous_usage_stats

    def track_struct_event(self, category: str, action: str) -> None:
        if not self.can_track():
            return

        if self.project.active_environment is not None:
            action = f"{action} --environment={hash_sha256(self.project.active_environment.name)}"

        try:
            self.snowplow_tracker.track_struct_event(
                category=category,
                action=action,
                label=self.project_id,
            )
        except Exception as ex:
            logger.warning(
                f"Failed to submit struct event to Snowplow:\n{traceback.format_exception(ex)}"
            )

    def track_unstruct_event(self, event_json: SelfDescribingJson) -> None:
        if not self.can_track():
            return
        try:
            self.snowplow_tracker.track_unstruct_event(event_json, self.contexts)
        except Exception as ex:
            logger.warning(
                f"Failed to submit unstruct event to Snowplow:\n{traceback.format_exception(ex)}"
            )

    def track_command_event(self, event_json: dict[str, Any]) -> None:
        self.track_unstruct_event(
            SelfDescribingJson(
                "iglu:com.meltano/command_event/jsonschema/1-0-0", event_json
            )
        )
