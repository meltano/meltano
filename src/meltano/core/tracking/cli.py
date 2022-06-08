"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

from snowplow_tracker import SelfDescribingJson

CLI_CONTEXT_SCHEMA = "iglu:com.meltano/cli_context/jsonschema"
CLI_CONTEXT_SCHEMA_VERSION = "1-0-0"

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


def cli_context_builder(
    command: str, sub_command: str | None = None, **kwargs
) -> CliContext:
    """Initialize a CLI context.

    Args:
        command: The CLI command.
        sub_command: The CLI sub command.
        kwargs: Additional key-value pairs to evaluate as option_keys if they are not None/False.

    Returns:
        A CLI context.
    """
    option_keys = [key for key, val in kwargs.items() if val]
    return CliContext(command=command, sub_command=sub_command, option_keys=option_keys)


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
            f"{CLI_CONTEXT_SCHEMA}/{CLI_CONTEXT_SCHEMA_VERSION}",
            {
                "command": command,
                "sub_command": sub_command,
                "option_keys": option_keys or [],
            },
        )
