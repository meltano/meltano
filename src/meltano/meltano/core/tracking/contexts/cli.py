"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

from enum import Enum, auto

import click
from snowplow_tracker import SelfDescribingJson

from meltano.core.tracking.schemas import CliContextSchema
from meltano.core.utils import hash_sha256


class CliEvent(Enum):
    """The kind of event that is occurring in the command-line interface."""

    # The cli command has started, this is fired automatically in most cases when the command is called.
    started = auto()
    # Optionally, a command may fire a `inflight` event to signal that its execution is in progress. This is useful for
    # commands that are long-running and may take a long time to finish, and allows them to emit an event with collected
    # contexts.
    inflight = auto()
    # The cli command has completed without errors.
    completed = auto()
    # Not used in practice.
    skipped = auto()
    # The cli command has failed to complete
    failed = auto()
    # The cli command aborted due to a user induced error.
    aborted = auto()


class CliContext(SelfDescribingJson):
    """CLI context for the Snowplow tracker."""

    def __init__(
        self,
        command: str,
        parent_command_hint: str | None = None,
        options: dict | None = None,
    ):
        """Initialize a CLI context.

        Args:
            command: The command name e.g. `schedule` or `list`.
            parent_command_hint: The upstream parent command e.g. `cli`, `schedule`.
            options: A dict of options keys and sanitized values.
        """
        super().__init__(
            CliContextSchema.url,
            {
                "command": command,
                "parent_command_hint": parent_command_hint,
                "options": options or {},
            },
        )

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> CliContext:
        """Initialize a CLI context.

        Args:
            ctx: The click.Context to derive our tracking context from.

        Returns:
            A CLI context.
        """
        options = {}
        for key, val in ctx.params.items():
            if isinstance(val, (bool, int, float)) or val is None:
                options[key] = val
            else:
                options[key] = hash_sha256(repr(val))

        return cls(
            command=ctx.command.name,
            parent_command_hint=ctx.parent.command.name if ctx.parent else None,
            options=options,
        )
