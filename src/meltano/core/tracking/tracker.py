"""Meltano telemetry."""

from __future__ import annotations

import datetime
import locale
import re
from contextlib import contextmanager
from enum import Enum, auto
from typing import Any
from urllib.parse import urlparse

import tzlocal
from cached_property import cached_property
from snowplow_tracker import Emitter, SelfDescribingJson
from snowplow_tracker import Tracker as SnowplowTracker
from structlog.stdlib import get_logger

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.project import ProjectContext
from meltano.core.utils import hash_sha256

from .environment import environment_context

CLI_EVENT_SCHEMA = "iglu:com.meltano/cli_event/jsonschema"
CLI_EVENT_SCHEMA_VERSION = "1-0-0"
BLOCK_EVENT_SCHEMA = "iglu:com.meltano/block_event/jsonschema"
BLOCK_EVENT_SCHEMA_VERSION = "1-0-0"


class BlockEvents(Enum):
    """Events describing a block state."""

    initialized = auto()
    started = auto()
    completed = auto()
    failed = auto()


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
class Tracker:
    """Meltano tracker backed by Snowplow."""

    def __init__(
        self,
        project: Project,
        request_timeout: float | tuple[float, float] | None = None,
    ):
        """Initialize a tracker for the Meltano project.

        Args:
            project: The Meltano project.
            request_timeout: Timeout for the HTTP requests. Can be set either as single float value which applies to both `connect` AND `read` timeout, or as tuple with two float values which specify the `connect` and `read` timeouts separately.
        """
        self.project = project
        self.settings_service = ProjectSettingsService(project)

        # TODO: do we want different endpoints when the release marker is not present?
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
            self.snowplow_tracker = SnowplowTracker(emitters=emitters)
            self.snowplow_tracker.subject.set_lang(locale.getdefaultlocale()[0])
            self.snowplow_tracker.subject.set_timezone(self.timezone_name)
        else:
            self.snowplow_tracker = None

        self.send_anonymous_usage_stats = self.settings_service.get(
            "send_anonymous_usage_stats", True
        )

        project_ctx = ProjectContext(project)
        self.project_id = str(project_ctx.project_uuid)
        self.contexts: tuple[SelfDescribingJson] = (
            environment_context,
            project_ctx,
        )

    @cached_property
    def timezone_name(self) -> str:
        """Obtain the local timezone name.

        Examples:
            The timezone name as an IANA timezone database name:

                >>> SnowplowTracker(project).timezone_name
                'Europe/Berlin'

            The timezone name as an IANA timezone abbreviation because the full name was not found:

                >>> SnowplowTracker(project).timezone_name
                'CET'

        Returns:
            The local timezone as an IANA TZ database name if possible, or abbreviation otherwise.
        """
        try:
            return tzlocal.get_localzone_name()
        except Exception:
            return datetime.datetime.now().astimezone().tzname()

    @contextmanager
    def with_contexts(self, *extra_contexts) -> Tracker:
        """Context manager within which the `Tracker` has additional Snowplow contexts.

        Args:
            extra_contexts: The additional contexts to add to the `Tracker`.

        Yields:
            A `Tracker` with additional Snowplow contexts.
        """
        prev_contexts = self.contexts
        self.contexts = (*prev_contexts, *extra_contexts)
        try:
            yield self
        finally:
            self.contexts = prev_contexts

    def can_track(self) -> bool:
        """Check if the tracker can be used.

        Returns:
            True if the tracker can be used, False otherwise.
        """
        return self.snowplow_tracker is not None and self.send_anonymous_usage_stats

    def track_struct_event(self, category: str, action: str) -> None:
        """Fire a structured tracking event.

        Note: This is a legacy method that will be removed in a future version, once LegacyTracker is no longer used.

        Args:
            category: The category of the event.
            action: The event actions.
        """
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
        except Exception as err:
            logger.debug("Failed to submit struct event to Snowplow", err=err)

    def track_unstruct_event(self, event_json: SelfDescribingJson) -> None:
        """Fire an unstructured tracking event.

        Args:
            event_json: The SelfDescribingJson event to track. See the Snowplow documentation for more information.
        """
        if not self.can_track():
            return
        try:
            self.snowplow_tracker.track_unstruct_event(event_json, self.contexts)
        except Exception as err:
            logger.debug("Failed to submit unstruct event to Snowplow, error", err=err)

    def track_command_event(self, event_json: dict[str, Any]) -> None:
        """Fire generic command tracking event.

        Args:
            event_json: The event JSON to track. See cli_event schema for more details.
        """
        self.track_unstruct_event(
            SelfDescribingJson(
                f"{CLI_EVENT_SCHEMA}/{CLI_EVENT_SCHEMA_VERSION}", event_json
            )
        )

    def track_block_event(self, block_type: str, event: BlockEvents) -> None:
        """Fire generic block tracking event.

        Args:
            block_type: The block type.
            event: The event string (e.g. "initialize", "started", etc)
        """
        self.track_unstruct_event(
            SelfDescribingJson(
                f"{BLOCK_EVENT_SCHEMA}/{BLOCK_EVENT_SCHEMA_VERSION}",
                {"type": block_type, "event": event.name},
            )
        )
