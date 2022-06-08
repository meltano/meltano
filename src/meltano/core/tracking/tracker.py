"""Meltano telemetry."""

from __future__ import annotations

import datetime
import json
import locale
import re
import uuid
from contextlib import contextmanager
from enum import Enum, auto
from pathlib import Path
from typing import Any, NamedTuple, Optional
from urllib.parse import urlparse

import tzlocal
from cached_property import cached_property
from snowplow_tracker import Emitter, SelfDescribingJson
from snowplow_tracker import Tracker as SnowplowTracker
from structlog.stdlib import get_logger

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.tracking.project import ProjectContext
from meltano.core.utils import format_exception, hash_sha256

from .environment import environment_context

CLI_EVENT_SCHEMA = "iglu:com.meltano/cli_event/jsonschema"
CLI_EVENT_SCHEMA_VERSION = "1-0-0"
TELEMETRY_STATE_CHANGE_EVENT_SCHEMA = (
    "iglu:com.meltano/telemetry_state_change_event/jsonschema"
)
TELEMETRY_STATE_CHANGE_EVENT_SCHEMA_VERSION = "1-0-0"
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


class TelemetrySettings(NamedTuple):
    """Settings which control telemetry and anonymous usage stats.

    These are stored within `analytics.json`.
    """

    client_id: uuid.UUID | None
    project_id: uuid.UUID | None
    send_anonymous_usage_stats: bool | None


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

        stored_telemetry_settings = self.load_saved_telemetry_settings()
        self.client_id = stored_telemetry_settings.client_id or uuid.uuid4()

        project_ctx = ProjectContext(project, self.client_id)
        self.project_id: uuid.UUID = project_ctx.project_uuid
        self.contexts: tuple[SelfDescribingJson] = (
            environment_context,
            project_ctx,
        )

        self.telemetry_state_change_check(stored_telemetry_settings)

    @cached_property
    def send_anonymous_usage_stats(self) -> bool:
        """Return whether anonymous usages stats are enabled (bool).

        - Return the value from 'send_anonymous_usage_stats', if set.
        - Otherwise the opposite of 'tracking_disabled', if set.
        - Otherwise return 'True'

        Returns:
            True if anonymous usage stats are enabled.
        """
        if self.settings_service.get("send_anonymous_usage_stats", None) is not None:
            return self.settings_service.get("send_anonymous_usage_stats")

        if self.settings_service.get("tracking_disabled", None) is not None:
            return not self.settings_service.get("tracking_disabled")

        return True

    def telemetry_state_change_check(
        self, stored_telemetry_settings: TelemetrySettings
    ) -> None:
        """Check prior values against current ones, and send a change event if needed.

        Args:
            stored_telemetry_settings: the prior analytics settings
        """
        save_settings = False

        if (
            stored_telemetry_settings.send_anonymous_usage_stats is None
            and not self.send_anonymous_usage_stats
        ):
            # Do nothing. Tracking is disabled and no tracking marker to update.
            return

        if (
            stored_telemetry_settings.project_id is not None
            and stored_telemetry_settings.project_id != self.project_id
        ):
            # Project ID has changed
            self.track_telemetry_state_change_event(
                "project_id", stored_telemetry_settings.project_id, self.project_id
            )
            save_settings = True

        if (
            stored_telemetry_settings.send_anonymous_usage_stats is not None
            and stored_telemetry_settings.send_anonymous_usage_stats
            != self.send_anonymous_usage_stats
        ):
            # Telemetry state has changed
            self.track_telemetry_state_change_event(
                "project_id",
                stored_telemetry_settings.send_anonymous_usage_stats,
                self.send_anonymous_usage_stats,
            )
            save_settings = True

        if save_settings:
            self.save_telemetry_settings()

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
                label=str(self.project_id),
            )
        except Exception as err:
            logger.debug(
                "Failed to submit struct event to Snowplow",
                err=format_exception(err),
            )

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
            logger.debug(
                "Failed to submit unstruct event to Snowplow, error",
                err=format_exception(err),
            )

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

    def track_telemetry_state_change_event(
        self,
        setting_name: str,
        from_value: uuid.UUID | str | bool | None,
        to_value: uuid.UUID | str | bool | None,
    ) -> None:
        """Fire a telemetry state change event.

        Args:
            setting_name: the name of the setting that is changing
            from_value: the old value
            to_value: the new value
        """
        logger.debug(
            "Telemetry state change detected. A one-time "
            + "'telemetry_state_change' event will now be sent.",
            setting_name=setting_name,
        )
        if isinstance(from_value, uuid.UUID):
            from_value = str(from_value)
        if isinstance(to_value, uuid.UUID):
            to_value = str(to_value)
        event_json = SelfDescribingJson(
            f"{TELEMETRY_STATE_CHANGE_EVENT_SCHEMA}/{TELEMETRY_STATE_CHANGE_EVENT_SCHEMA_VERSION}",
            {
                "setting_name": setting_name,
                "changed_from": from_value,
                "changed_to": to_value,
            },
        )
        try:
            self.snowplow_tracker.track_unstruct_event(
                event_json,
                # Provide no Snowplow contexts so as to avoid sending any extra information beyond
                # the 'telemetry_state_change' event.
                None,
            )
        except Exception as err:
            logger.debug(
                "Failed to submit 'telemetry_state_change' unstruct event to Snowplow, error",
                err=format_exception(err),
            )

    @property
    def analytics_json_path(self) -> Path:
        """Return path to the 'analytics.json' file.

        Returns:
            Path to 'analytics.json' file.
        """
        return self.project.meltano_dir() / "analytics.json"

    def load_saved_telemetry_settings(self) -> TelemetrySettings:
        """Get settings from the 'analytics.json' file.

        Returns:
            The saved telemetry settings.
        """
        try:
            with open(self.analytics_json_path) as analytics_json_file:
                analytics = json.load(analytics_json_file)
        except FileNotFoundError:
            return TelemetrySettings(None, None, None)
        return TelemetrySettings(
            self._uuid_from_str(analytics.get("client_id"), warn=True),
            self._uuid_from_str(analytics.get("project_id"), warn=True),
            analytics.get("send_anonymous_usage_stats"),
        )

    def save_telemetry_settings(self) -> None:
        """Save settings to the 'analytics.json' file."""
        with open(self.analytics_json_path, "w") as new_analytics_json_file:
            json.dump(
                {
                    "client_id": str(self.client_id),
                    "project_id": str(self.project_id),
                    "send_anonymous_usage_stats": self.send_anonymous_usage_stats,
                },
                new_analytics_json_file,
            )

    def _uuid_from_str(self, from_val: Optional[Any], warn: bool) -> uuid.UUID | None:
        """Safely convert string to a UUID. Return None if invalid UUID.

        Args:
            from_val: The string.
            warn: True to warn on conversion failure.

        Returns:
            A UUID object, or None if the string cannot be converted to UUID.
        """
        if not isinstance(from_val, str):
            if from_val is None:
                return None

            logger.warning(
                "Unexpected value type in 'analytics.json'",
                expected_type="string",
                value_type=type(from_val),
                value=from_val,
            )

        try:
            return uuid.UUID(from_val)
        except ValueError:
            # Should only be reached if user manually edits 'analytics.json'.
            log_fn = logger.warning if warn else logger.debug
            log_fn(
                "Invalid UUID string in 'analytics.json'",
                value=from_val,
            )
            return None

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
