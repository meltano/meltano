"""Legacy tracker for Meltano.

This module and its content will be removed in a future version of Meltano without a major version
bump. It only remains here to make the transition to the new tracker as smooth as possible.
"""

from __future__ import annotations

from typing import Any

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.schedule import Schedule
from meltano.core.tracking import Tracker
from meltano.core.tracking.project import ProjectContext
from meltano.core.utils import hash_sha256

REQUEST_TIMEOUT = 2.0
MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/collect"
DEBUG_MEASUREMENT_PROTOCOL_URI = "https://www.google-analytics.com/debug/collect"


class LegacyTracker:
    """Legacy tracker for Meltano."""

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

        self.tracker = Tracker(
            project,
            request_timeout=self.request_timeout,
        )

        project_context = ProjectContext(project, self.tracker.client_id)
        self.project_id = project_context.project_uuid

    def event(self, category: str, action: str) -> dict[str, Any]:
        """Construct a GA event with all the required parameters.

        Args:
            category: The category of the event.
            action: The action of the event.

        Returns:
            A dict with all the required parameters.
        """
        return {
            "v": "1",
            "tid": self.tracking_id,
            "cid": self.tracker.client_id,
            "ds": "meltano cli",
            "t": "event",
            "ec": category,
            "ea": action,
            "el": self.project_id,
            "cd1": self.project_id,  # maps to the custom dimension 1 of the UI
        }

    def track_event(self, category: str, action: str, debug: bool = False) -> None:
        """Send a struct event to Snowplow.

        Args:
            category: GA event category.
            action: GA event action.
            debug: If True, send the event to the debug endpoint.
        """
        self.tracker.track_struct_event(category, action)

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
            if schedule.job:
                self.track_event(
                    category="meltano schedule",
                    action=(
                        f"meltano schedule {action} {schedule.name} "
                        + f"--job={schedule.job} --interval={schedule.interval}"
                    ),
                    debug=debug,
                )
            else:
                self.track_event(
                    category="meltano schedule",
                    action=(
                        f"meltano schedule {action} {schedule.name} "
                        + f"--extractor {schedule.extractor} --loader {schedule.loader} --interval {schedule.interval} "
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

    def track_meltano_state(self, subcommand: str, state_id: str | None = None):
        """Track the management of Singer State.

        Args:
            subcommand: The subcommand being run (e.g. 'set' or 'clear')
            state_id: The state_id for which state is being managed
        """
        action = f"meltano state {subcommand}"
        if state_id:
            hashed_state_id = hash_sha256(state_id)
            action = f"{action} {hashed_state_id}"
        self.track_event(category="meltano state", action=action)

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

    def track_meltano_job(
        self, action: str, job_name: str | None = None, debug: bool = False
    ) -> None:
        """Track a job event.

        Args:
            action: The type of action taken on the job (e.g. add, run, list)
            job_name: The job to track.
            debug: Whether to send the event to the debug endpoint.
        """
        if job_name:
            self.track_event(
                category="meltano job",
                action=(f"meltano job {job_name} {action} "),
                debug=debug,
            )
        else:
            self.track_event(
                category="meltano job",
                action=f"meltano job {action}",
                debug=debug,
            )
