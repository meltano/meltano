"""Google Analytics tracker for CLI commands."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from typing import Any

import requests

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.schedule import Schedule

from .snowplow_tracker import SnowplowTracker

REQUEST_TIMEOUT = 2.0
MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/collect"
DEBUG_MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/debug/collect"


class GoogleAnalyticsTracker:  # noqa: WPS214, WPS230
    """Event tracker for Meltano."""

    def __init__(
        self,
        project: Project,
        tracking_id: str = None,
        request_timeout: float = None,
    ):
        """Create a new Google Analytics tracker.

        Args:
            project: Meltano project.
            tracking_id: Unique identifier for tracking. Defaults to None.
            request_timeout: For GA requests. Defaults to None.
        """
        self.project = project
        self.settings_service = ProjectSettingsService(self.project)

        self.tracking_id = tracking_id or self.settings_service.get("tracking_ids.cli")
        self.request_timeout = request_timeout or REQUEST_TIMEOUT

        self.send_anonymous_usage_stats = self.settings_service.get(
            "send_anonymous_usage_stats", True
        )
        self.project_id = self.load_project_id()
        self.client_id = self.load_client_id()

        try:
            self.snowplow_tracker = SnowplowTracker(
                project,
                request_timeout=self.request_timeout,
            )
        except ValueError:
            logging.debug("No Snowplow collector endpoints are set")
            self.snowplow_tracker = None

    def load_project_id(self) -> uuid.UUID:
        """
        Fetch the project_id from the project config file.

        If it is not found (e.g. first time run), generate a valid uuid4 and
        store it in the project config file.

        Returns:
            The project_id.
        """
        project_id_str = self.settings_service.get("project_id")
        try:
            project_id = uuid.UUID(project_id_str or "", version=4)
        except ValueError:
            project_id = uuid.uuid4()

            if self.send_anonymous_usage_stats:
                # If we are set to track Anonymous Usage stats, also store
                #  the generated project_id back to the project config file
                #  so that it persists between meltano runs.
                self.settings_service.set("project_id", str(project_id))

        return project_id

    def load_client_id(self) -> uuid.UUID:
        """
        Fetch the client_id from the non-versioned analytics.json.

        If it is not found (e.g. first time run), generate a valid uuid4 and
        store it in analytics.json.

        Returns:
            The client_id.
        """
        file_path = self.project.meltano_dir().joinpath("analytics.json")
        try:  # noqa: WPS229
            with open(file_path) as file:
                file_data = json.load(file)
            client_id_str = file_data["client_id"]
            client_id = uuid.UUID(client_id_str, version=4)
        except FileNotFoundError:
            client_id = uuid.uuid4()

            if self.send_anonymous_usage_stats:
                # If we are set to track Anonymous Usage stats, also store
                #  the generated client_id in a non-versioned analytics.json file
                #  so that it persists between meltano runs.
                with open(file_path, "w") as file:  # noqa: WPS440
                    data = {"client_id": str(client_id)}
                    json.dump(data, file)

        return client_id

    def event(self, category: str, action: str) -> dict[str, Any]:
        """Constract a GA event with all the required parameters.

        Args:
            category: The category of the event.
            action: The action of the event.

        Returns:
            A dict with all the required parameters.
        """
        return {
            "v": "1",
            "tid": self.tracking_id,
            "cid": self.client_id,
            "ds": "meltano cli",
            "t": "event",
            "ec": category,
            "ea": action,
            "el": self.project_id,
            "cd1": self.project_id,  # maps to the custom dimension 1 of the UI
        }

    def track_data(  # noqa: WPS213
        self, data: dict[str, Any], debug: bool = False
    ) -> None:
        """Send usage statistics back to Google Analytics.

        Args:
            data: The data to send.
            debug: Whether to send the event to the debug endpoint.
        """
        if self.send_anonymous_usage_stats is False:
            # Only send anonymous usage stats if you have explicit permission
            return

        if debug:
            tracking_uri = DEBUG_MEASUREMENT_PROTOCOL_URI
        else:
            tracking_uri = MEASUREMENT_PROTOCOL_URI

        try:  # noqa: WPS229
            resp = requests.post(tracking_uri, data=data, timeout=self.request_timeout)

            if debug:
                logging.debug("GoogleAnalyticsTracker.track_data:")
                logging.debug(data)
                logging.debug("Response:")
                logging.debug(f"status_code: {resp.status_code}")
                logging.debug(resp.text)
        except requests.exceptions.Timeout:
            logging.debug("GoogleAnalyticsTracker.track_data: Request Timed Out")
        except requests.exceptions.ConnectionError as exc:
            logging.debug("GoogleAnalyticsTracker.track_data: ConnectionError")
            logging.debug(exc)
        except requests.exceptions.RequestException as exc:
            logging.debug("GoogleAnalyticsTracker.track_data: RequestException")
            logging.debug(exc)

    def track_event(self, category: str, action: str, debug: bool = False) -> None:
        """Send a GA event.

        Args:
            category: GA event category.
            action: GA event action.
            debug: If True, send the event to the debug endpoint.
        """
        if self.project.active_environment is not None:
            environment = self.project.active_environment
            hashed_name = hashlib.sha256(environment.name.encode()).hexdigest()
            action = f"{action} --environment={hashed_name}"

        event = self.event(category, action)
        self.track_data(event, debug)

        # Snowplow
        self.track_snowplow_struct_event(category=category, action=action)

    def track_snowplow_struct_event(self, category: str, action: str) -> None:
        """Send a struct event to Snowplow.

        Args:
            category: The category of the event.
            action: The action of the event.
        """
        if self.send_anonymous_usage_stats is False or self.snowplow_tracker is None:
            # Only send anonymous usage stats if you have explicit permission
            return

        self.snowplow_tracker.track_struct_event(
            category=category,
            action=action,
            label=self.project_id,
        )

    def track_meltano_init(self, project_name: str, debug: bool = False) -> None:
        """Track the initialization of a Meltano project.

        Args:
            project_name: The name of the project.
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category="meltano init", action=f"meltano init {project_name}", debug=debug
        )

    def track_meltano_add(
        self, plugin_type: str, plugin_name: str, debug: bool = False
    ) -> None:
        """Track a plugin add event.

        Args:
            plugin_type: The type of the plugin.
            plugin_name: The name of the plugin.
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category=f"meltano add {plugin_type}",
            action=f"meltano add {plugin_type} {plugin_name}",
            debug=debug,
        )

    def track_meltano_discover(self, plugin_type: str, debug: bool = False) -> None:
        """Track the discovery of a plugin type.

        Args:
            plugin_type: The type of plugin that was discovered.
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category="meltano discover",
            action=f"meltano discover {plugin_type}",
            debug=debug,
        )

    def track_meltano_elt(
        self, extractor: str, loader: str, transform: str, debug: bool = False
    ) -> None:
        """Track a meltano elt command.

        Args:
            extractor: The extractor name.
            loader: The loader name.
            transform: The transform name.
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category="meltano elt",
            action=f"meltano elt {extractor} {loader} --transform {transform}",
            debug=debug,
        )

    def track_meltano_install(self, debug: bool = False) -> None:
        """Track the installation of plugins.

        Args:
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category="meltano install", action="meltano install", debug=debug
        )

    def track_meltano_invoke(
        self, plugin_name: str, plugin_args: str, debug: bool = False
    ) -> None:
        """Track a meltano invoke event.

        Args:
            plugin_name: The name of the plugin invoked.
            plugin_args: The arguments passed to the plugin.
            debug: Whether to send the event to the debug endpoint.
        """
        self.track_event(
            category="meltano invoke",
            action=f"meltano invoke {plugin_name} {plugin_args}",
            debug=debug,
        )

    def track_meltano_schedule(
        self, action: str, schedule: Schedule | None = None, debug: bool = False
    ) -> None:
        """Track a schedule event.

        Args:
            action: The type of action taken on the schedule (e.g. add, run, list)
            schedule: The schedule to track.
            debug: Whether to send the event to the debug endpoint.
        """
        if schedule:
            self.track_event(
                category="meltano schedule",
                action=(
                    f"meltano schedule {action} {schedule.name} "
                    + f"{schedule.extractor} {schedule.loader} {schedule.interval} "
                    + f"--transform={schedule.transform}"
                ),
                debug=debug,
            )
        else:
            self.track_event(
                category="meltano schedule",
                action=(f"meltano schedule {action}"),
                debug=debug,
            )

    def track_meltano_select(
        self,
        extractor: str,
        entities_filter: str,
        attributes_filter: str,
        flags: dict[str, bool],
        debug: bool = False,
    ) -> None:
        """Track the selection of entities and attributes.

        Args:
            extractor: The extractor name.
            entities_filter: The entities filter.
            attributes_filter: The attributes filter.
            flags: The CLI flags.
            debug: Whether to send the event to the debug endpoint.
        """
        action = f"meltano select {extractor} {entities_filter} {attributes_filter}"

        if flags["list"]:
            action = f"{action} --list"
        if flags["all"]:
            action = f"{action} --all"
        if flags["exclude"]:
            action = f"{action} --exclude"

        self.track_event(category="meltano select", action=action, debug=debug)

    def track_meltano_ui(self, debug: bool = False) -> None:
        """Track the UI start-up.

        Args:
            debug: Whether to send the event to the debug endpoint.
        """
        action = "meltano ui"
        self.track_event(category="meltano ui", action=action, debug=debug)

    def track_meltano_test(
        self,
        plugin_tests: tuple[str],
        debug: bool = False,
        **flags: dict[str, bool],
    ) -> None:
        """Track invocations of `meltano test`.

        Args:
            plugin_tests: A tuple of plugin names and test names.
            debug: Whether to send the event to the debug endpoint.
            flags: A dictionary of CLI flags.
        """
        action = "meltano test"

        if flags["all_tests"]:
            action = f"{action} --all"

        for plugin_test in plugin_tests:
            action = f"{action} {plugin_test}"

        self.track_event(
            category="meltano test",
            action=action,
            debug=debug,
        )

    def track_meltano_run(self, blocks: list[str], debug: bool = False) -> None:
        """Track invocations of `meltano run`.

        Args:
            blocks: The blocks to track.
            debug: Whether to print debug information.
        """
        blocks_string = " ".join(blocks)
        self.track_event(
            category="meltano run",
            action=f"meltano run {blocks_string}",
            debug=debug,
        )
