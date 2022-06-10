"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

from enum import Enum, auto

from snowplow_tracker import SelfDescribingJson

from meltano.core.tracking.schemas import CliContextSchema


class CliEvent(Enum):
    """The kind of event that is occuring in the command-line interface."""

    started = auto()
    completed = auto()
    skipped = auto()
    failed = auto()
    aborted = auto()


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
            CliContextSchema.url,
            {
                "command": command,
                "sub_command": sub_command,
                "option_keys": option_keys or [],
            },
        )
