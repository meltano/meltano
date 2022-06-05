"""Meltano telemetry."""

from __future__ import annotations

import datetime
import json
import locale
import re
import uuid
from contextlib import contextmanager
from linecache import cache
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
    def send_anonymous_usage_stats(self) -> bool:
        """Return whether anonymous usages stats are enabled (bool).

        - Return the value from 'send_anonymous_usage_stats', if set.
        - Otherwise the opposite of 'tracking_disabled', if set.
        - Otherwise return 'True'

        """
        if self.settings_service.get("send_anonymous_usage_stats", None) is not None:
            return self.settings_service.get("send_anonymous_usage_stats")
        if self.settings_service.get("tracking_disabled", None) is not None:
            return not self.settings_service.get("tracking_disabled")

        return True

    def sync_analytics_settings(self) -> None:
        """Returns a dict with client_id, project_id, and send_anonymous_usage_stats."""
        analytics_json_path = self.project.meltano_dir() / "analytics.json"
        try:
            with open(analytics_json_path, encoding="utf-8") as analytics_json_file:
                analytics_json = json.load(analytics_json_file)
        except FileNotFoundError:
            if not self.send_anonymous_usage_stats:
                # Tracking disabled and no tracking file to update.
                return

            # Tracking is enabled and no 'analytics.json' file exists.
            # Store the generated `client_id` along with `project_id` and
            # `send_anonymous_usage_stats=True` in a non-versioned `analytics.json` file
            # so that it persists between meltano runs.
            self._save_analytics_settings(
                client_id=uuid.uuid4(),
                project_id=self.project_uuid(),
                send_anonymous_usage_stats=True,
            )
            return

        # File does exist. Read existing settings.
        client_id = analytics_json.get("client_id", uuid.uuid4())
        project_id = analytics_json.get("project_id", self.project_uuid())
        send_anonymous_usage_stats = analytics_json.get(
            "send_anonymous_usage_stats", self.send_anonymous_usage_stats
        )
        self._telemetry_state_change_check(
            project=project,
            prior_project_id=project_id,
            prior_send_anonymous_usage_stats_val=send_anonymous_usage_stats,
        )
        self._save_analytics_settings(
            client_id=client_id,
            project_id=project_id,
            send_anonymous_usage_stats=send_anonymous_usage_stats,
        )

    def _save_analytics_settings(
        self, client_id: str, project_id: str, send_anonymous_usage_stats: bool
    ) -> None:
        analytics_json_path = self.project.meltano_dir() / "analytics.json"
        with open(
            analytics_json_path, "w", encoding="utf-8"
        ) as new_analytics_json_file:
            json.dump(
                {
                    "client_id": str(client_id),
                    "project_id": str(project_id),
                    "send_anonymous_usage_stats": send_anonymous_usage_stats,
                },
                new_analytics_json_file,
            )

    def _telemetry_state_change_check(
        self, project, prior_project_id, prior_send_anonymous_usage_stats_val
    ) -> None:
        """Check prior values against current ones and send a change event if needed."""
        if (
            prior_project_id == self.project_uuid()
            and prior_send_anonymous_usage_stats_val == self.send_anonymous_usage_stats
        ):
            # No change. Nothing to do.
            return

        logger.debug(
            "Telemetry state change detected. "
            "A one time telemetry_state_change event will now be sent."
        )
        tracker = Tracker(project)
        cmd_ctx = CliContext("invoke")
        with tracker.with_contexts(cmd_ctx):
            tracker.track_command_event({"event": "started"})

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

    # TODO: Move this up one level, to the Tracker class
    @cached_property
    def client_uuid(self) -> uuid.UUID:
        """Obtain the `client_id` from the non-versioned `analytics.json`.

        If it is not found (e.g. first time run), generate a valid v4 UUID, and store it in
        `analytics.json`.

        Returns:
            The client UUID.
        """
        analytics_json_path = self.project.meltano_dir() / "analytics.json"
        try:
            with open(analytics_json_path) as analytics_json_file:
                analytics_json = json.load(analytics_json_file)
        except FileNotFoundError:
            client_id = uuid.uuid4()

            if self.send_anonymous_usage_stats:
                # If we are set to track Anonymous Usage stats, also store the generated
                # `client_id` in a non-versioned `analytics.json` file so that it persists between
                # meltano runs.
                with open(analytics_json_path, "w") as new_analytics_json_file:
                    json.dump({"client_id": str(client_id)}, new_analytics_json_file)
        else:
            client_id = uuid.UUID(analytics_json["client_id"], version=4)

        return client_id
