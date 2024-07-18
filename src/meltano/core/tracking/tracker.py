"""Meltano telemetry."""

from __future__ import annotations

import atexit
import json
import locale
import os
import re
import typing as t
import uuid
from contextlib import contextmanager, suppress
from datetime import datetime, timezone
from enum import Enum, auto
from urllib.parse import urlparse
from warnings import warn

import requests
import structlog
import tzlocal
from psutil import Process
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from meltano._vendor.snowplow_tracker import (  # noqa: WPS436
    Emitter,
    SelfDescribing,
    SelfDescribingJson,
)
from meltano._vendor.snowplow_tracker import Tracker as SnowplowTracker  # noqa: WPS436
from meltano.core.tracking.schemas import (
    BlockEventSchema,
    CliEventSchema,
    ExitEventSchema,
    TelemetryStateChangeEventSchema,
)
from meltano.core.utils import format_exception

if t.TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from meltano.core.project import Project
    from meltano.core.tracking.contexts import (  # noqa: F401
        CliEvent,
        EnvironmentContext,
        ProjectContext,
    )

from functools import cached_property

URL_REGEX = (
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

MICROSECONDS_PER_SECOND = 1000000

logger = structlog.get_logger(__name__)


class BlockEvents(Enum):
    """Events describing a block state."""

    initialized = auto()
    started = auto()
    completed = auto()
    failed = auto()


def check_url(url: str) -> bool:
    """Check if the given URL is valid.

    Args:
        url: The URL to check.

    Returns:
        True if the URL is valid, False otherwise.
    """
    return bool(re.match(URL_REGEX, url))


class TelemetrySettings(t.NamedTuple):
    """Settings which control telemetry and anonymous usage stats.

    These are stored within `analytics.json`.
    """

    client_id: uuid.UUID | None
    project_id: uuid.UUID | None
    send_anonymous_usage_stats: bool | None


class Tracker:  # - too many (public) methods
    """Meltano tracker backed by Snowplow."""

    def __init__(  # - too many local variables, too many expressions
        self,
        project: Project,
        request_timeout: float | tuple[float, float] | None = 3.5,
    ):
        """Initialize a tracker for the Meltano project.

        Args:
            project: The Meltano project.
            request_timeout: Timeout for the HTTP requests. Can be set either
                as single float value which applies to both `connect` and
                `read` timeout, or as tuple with two float values which specify
                the `connect` and `read` timeouts separately.
        """
        from meltano.core.tracking.contexts import (
            ProjectContext,
            environment_context,
        )

        self.project = project
        self.send_anonymous_usage_stats = project.settings.get(
            "send_anonymous_usage_stats",
            redacted=not project.settings.get("disable_tracking"),
        )

        endpoints = project.settings.get("snowplow.collector_endpoints")

        session = requests.Session()

        # Retry failed requests up to 3 times, but don't retry on error status codes
        adapter = HTTPAdapter(max_retries=Retry(total=3, status=0))
        session.mount("http://", adapter)
        session.mount("https://", adapter)
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
                    session=session,
                ),
            )

        if emitters:
            self.snowplow_tracker = SnowplowTracker(
                namespace="meltano-core",
                app_id="meltano",
                emitters=emitters,
            )
            self.snowplow_tracker.subject.set_lang(locale.getlocale()[0])
            self.snowplow_tracker.subject.set_timezone(self.timezone_name)
            self.setup_exit_event()
        else:
            self.snowplow_tracker = None

        stored_telemetry_settings = self.load_saved_telemetry_settings()

        self.client_id = self.get_client_id(stored_telemetry_settings)

        project_ctx = ProjectContext(project, self.client_id)
        self.project_id: uuid.UUID = project_ctx.project_uuid
        self._contexts: tuple[SelfDescribingJson] = (
            environment_context,
            project_ctx,
        )

        # Environment variables to set in invoked processes for telemetry purposes
        self.env: Mapping[str, str] = {
            "MELTANO_PARENT_CONTEXT_UUID": environment_context.data["context_uuid"],
        }

        if all(setting is None for setting in stored_telemetry_settings):
            self.save_telemetry_settings()
        else:
            self.telemetry_state_change_check(stored_telemetry_settings)
            if self.client_id != stored_telemetry_settings.client_id:
                self.save_telemetry_settings()

    def get_client_id(self, stored_telemetry_settings: TelemetrySettings) -> uuid.UUID:
        """Get the telemetry client ID.

        It can be set using the `$MELTANO_CLIENT_ID` environment variable. If
        that environment variable has not been set, then the client ID stored
        on disk will be used if it exists. If the client ID has not been stored
        on disk, then a new one will be randomly generated.

        Args:
            stored_telemetry_settings: The telemetry settings stored on disk.

        Returns:
            The client ID.
        """
        with suppress(KeyError):
            uuid_str = os.environ["MELTANO_CLIENT_ID"]
            try:
                return uuid.UUID(uuid_str)
            except ValueError:
                warn(
                    (
                        f"Invalid telemetry client UUID {uuid_str!r} from "
                        "$MELTANO_CLIENT_ID"
                    ),
                    RuntimeWarning,
                    stacklevel=2,
                )
        if stored_telemetry_settings.client_id is not None:
            return stored_telemetry_settings.client_id
        return uuid.uuid4()

    @property
    def contexts(self) -> tuple[SelfDescribingJson]:
        """Get the contexts that will accompany events fired by this tracker.

        Returns:
            The contexts that will accompany events fired by this tracker.
        """
        from meltano.core.tracking.contexts import ExceptionContext

        # The `ExceptionContext` is re-created every time this is accessed
        # because it details the exceptions that are being processed when it
        # is created.
        return (*self._contexts, ExceptionContext())

    def telemetry_state_change_check(
        self,
        stored_telemetry_settings: TelemetrySettings,
    ) -> None:
        """Check prior values against current ones, and send a change event if needed.

        Args:
            stored_telemetry_settings: the prior analytics settings
        """
        if (
            stored_telemetry_settings.project_id is not None
            and stored_telemetry_settings.project_id != self.project_id
            and self.send_anonymous_usage_stats
        ):
            # Project ID has changed
            self.track_telemetry_state_change_event(
                "project_id",
                stored_telemetry_settings.project_id,
                self.project_id,
            )

        if (
            stored_telemetry_settings.send_anonymous_usage_stats is not None
            and stored_telemetry_settings.send_anonymous_usage_stats
            != self.send_anonymous_usage_stats
        ):
            # Telemetry state has changed
            self.track_telemetry_state_change_event(
                "send_anonymous_usage_stats",
                stored_telemetry_settings.send_anonymous_usage_stats,
                self.send_anonymous_usage_stats,
            )

    @cached_property
    def timezone_name(self) -> str:
        """Obtain the local timezone name.

        Examples:
            The timezone name as an IANA timezone database name:

                >>> Tracker(project).timezone_name
                'Europe/Berlin'

            The timezone name as an IANA timezone abbreviation because the full
            name was not found:

                >>> Tracker(project).timezone_name
                'CET'

        Returns:
            The local timezone as an IANA TZ database name if possible, or
            abbreviation otherwise.
        """
        try:
            return tzlocal.get_localzone_name()
        except Exception:
            return datetime.now().astimezone().tzname()

    def add_contexts(self, *extra_contexts) -> None:  # noqa: ANN002
        """Permanently add additional Snowplow contexts to the `Tracker`.

        Args:
            extra_contexts: The additional contexts to add to the `Tracker`.
        """
        self._contexts = (*self._contexts, *extra_contexts)

    @contextmanager
    def with_contexts(self, *extra_contexts) -> Tracker:  # noqa: ANN002
        """Context manager within which the `Tracker` has additional Snowplow contexts.

        Args:
            extra_contexts: The additional contexts to add to the `Tracker`.

        Yields:
            A `Tracker` with additional Snowplow contexts.
        """
        prev_contexts = self._contexts
        self._contexts = (*prev_contexts, *extra_contexts)
        try:
            yield self
        finally:
            self._contexts = prev_contexts

    def can_track(self) -> bool:
        """Check if the tracker can be used.

        Returns:
            True if the tracker can be used, False otherwise.
        """
        return self.snowplow_tracker is not None and self.send_anonymous_usage_stats

    def track_unstruct_event(self, event_json: SelfDescribingJson) -> None:
        """Fire an unstructured tracking event.

        Args:
            event_json: The SelfDescribingJson event to track. See the Snowplow
                documentation for more information.
        """
        if not self.can_track():
            return
        try:
            self.snowplow_tracker.track(
                SelfDescribing(
                    event_json=event_json,
                    context=self.contexts,
                ),
            )
        except Exception as err:
            logger.debug(
                "Failed to submit unstruct event to Snowplow, error",
                err=format_exception(err),
            )

    def track_command_event(self, event: CliEvent) -> None:
        """Fire generic command tracking event.

        Args:
            event: An member from `meltano.core.tracking.CliEvent`
        """
        self.track_unstruct_event(
            SelfDescribingJson(CliEventSchema.url, {"event": event.name}),
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
        from meltano.core.tracking.contexts import (
            EnvironmentContext,
            ProjectContext,
        )

        # Save the telemetry settings to ensure this is the only telemetry
        # state change event fired for this particular setting change.
        self.save_telemetry_settings()

        if self.snowplow_tracker is None:
            # The Snowplow tracker is not available (e.g. because no endpoints are set)
            return

        logger.debug(
            (
                "Telemetry state change detected. A one-time "
                "'telemetry_state_change' event will now be sent."
            ),
            setting_name=setting_name,
        )
        if isinstance(from_value, uuid.UUID):
            from_value = str(from_value)
        if isinstance(to_value, uuid.UUID):
            to_value = str(to_value)
        event_json = SelfDescribingJson(
            TelemetryStateChangeEventSchema.url,
            {
                "setting_name": setting_name,
                "changed_from": from_value,
                "changed_to": to_value,
            },
        )
        try:
            self.snowplow_tracker.track(
                SelfDescribing(
                    event_json=event_json,
                    # If tracking is disabled, then include only the minimal
                    # Snowplow contexts required
                    context=self.contexts
                    if self.send_anonymous_usage_stats
                    else tuple(
                        ctx
                        for ctx in self.contexts
                        if isinstance(ctx, (EnvironmentContext, ProjectContext))
                    ),
                ),
            )
            self.snowplow_tracker.flush()
        except Exception as err:
            logger.debug(
                (
                    "Failed to submit 'telemetry_state_change' unstruct event "
                    "to Snowplow, error"
                ),
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
            with self.analytics_json_path.open() as analytics_json_file:
                analytics = json.load(analytics_json_file)
        except (OSError, json.JSONDecodeError):
            return TelemetrySettings(None, None, None)

        if missing_keys := {
            "client_id",
            "project_id",
            "send_anonymous_usage_stats",
        } - set(analytics):
            logger.debug(
                (
                    "'analytics.json' has missing keys, and will be "
                    "overwritten with new 'analytics.json'"
                ),
                missing_keys=missing_keys,
            )
            return TelemetrySettings(None, None, None)
        return TelemetrySettings(
            self._uuid_from_str(analytics.get("client_id"), warn=True),
            self._uuid_from_str(analytics.get("project_id"), warn=True),
            analytics.get("send_anonymous_usage_stats"),
        )

    def save_telemetry_settings(self) -> None:
        """Attempt to save settings to the 'analytics.json' file."""
        try:
            with self.analytics_json_path.open("w") as new_analytics_json_file:
                json.dump(
                    {
                        "client_id": str(self.client_id),
                        "project_id": str(self.project_id),
                        "send_anonymous_usage_stats": self.send_anonymous_usage_stats,
                    },
                    new_analytics_json_file,
                )
        except OSError as err:
            logger.debug("Unable to save 'analytics.json'", err=err)

    def _uuid_from_str(
        self,
        from_val: t.Any | None,  # noqa: ANN401
        *,
        warn: bool,
    ) -> uuid.UUID | None:
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
        except (ValueError, TypeError):
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
                BlockEventSchema.url,
                {"type": block_type, "event": event.name},
            ),
        )

    def setup_exit_event(self) -> None:
        """If not already done, register the atexit handler to fire the exit event.

        This method also provides this tracker instance to the CLI module for
        it to fire an exit event immediately before the CLI exits. The atexit
        handler is used only as a fallback.
        """
        from meltano import cli

        if cli.atexit_handler_registered:
            return

        cli.atexit_handler_registered = True

        # Provide `meltano.cli` with this tracker to track the exit event with
        # more context.
        cli.exit_event_tracker = self

        # As a fallback, use atexit to help ensure the exit event is sent.
        atexit.register(self.track_exit_event)

    def track_exit_event(self) -> None:
        """Fire exit event."""
        from meltano import cli

        if cli.exit_code_reported:
            return
        cli.exit_code_reported = True

        start_time = datetime.fromtimestamp(Process().create_time(), tz=timezone.utc)

        # This is the reported "end time" for this process, though in reality
        # the process will end a short time after this time as it takes time
        # to emit the event.
        now = datetime.now(timezone.utc)

        self.track_unstruct_event(
            SelfDescribingJson(
                ExitEventSchema.url,
                {
                    "exit_code": cli.exit_code,
                    "exit_timestamp": f"{now.isoformat()}",
                    "process_duration_microseconds": int(
                        (now - start_time).total_seconds() * MICROSECONDS_PER_SECOND,
                    ),
                },
            ),
        )
        self.snowplow_tracker.flush()
        atexit.unregister(self.track_exit_event)
