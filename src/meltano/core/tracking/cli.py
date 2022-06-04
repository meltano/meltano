"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

import uuid

from snowplow_tracker import SelfDescribingJson

EVENT_RESULTS = {
    "started": {"event": "started"},
    "completed": {"event": "completed"},
    "skipped": {"event": "skipped"},
    "failed": {"event": "failed"},
    "aborted": {"event": "aborted"},
}

STARTED = EVENT_RESULTS["started"]
COMPLETED = EVENT_RESULTS["completed"]
SKIPPED = EVENT_RESULTS["skipped"]
FAILED = EVENT_RESULTS["failed"]
ABORTED = EVENT_RESULTS["aborted"]


class CliContext(SelfDescribingJson):
    """CLI context for the Snowplow tracker."""

    def __init__(
        self,
        command: str,
        sub_command: str | None = None,
        option_keys: list(str) | None = None,
    ):
        """Initialize the CLI context.

        Args:
            command: The command name e.g. `schedule`.
            sub_command: The sub-command name `add` or `set`.
            option_keys: The list of option keys `loader`, `job`.
        """
        super().__init__(
            "iglu:com.meltano/cli_context/jsonschema/1-0-0",
            {
                "event_uuid": str(uuid.uuid4()),
                "command": command,
                "sub_command": sub_command,
                "option_keys": option_keys or [],
            },
        )
