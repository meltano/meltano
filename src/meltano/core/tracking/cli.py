"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

from snowplow_tracker import SelfDescribingJson


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
                "command": command,
                "sub_command": sub_command,
                "option_keys": option_keys or [],
            },
        )
