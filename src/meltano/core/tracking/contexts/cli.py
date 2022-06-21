"""Meltano telemetry contexts for the CLI events."""
from __future__ import annotations

from enum import Enum, auto

import click
from snowplow_tracker import SelfDescribingJson

from meltano.core.tracking.schemas import CliContextSchema
from meltano.core.utils import hash_sha256


class CliEvent(Enum):
    """The kind of event that is occuring in the command-line interface."""

    started = auto()
    completed = auto()
    skipped = auto()
    failed = auto()
    aborted = auto()


class CliContext(SelfDescribingJson):
    """CLI context for the Snowplow tracker."""

    def __init__(
        self,
        command: str,
        sub_command: str | None = None,
        option_keys: list(str) | None = None,
    ):
        """Initialize a CLI context.

        Args:
            command: The command name e.g. `schedule`.
            sub_command: The sub-command name e.g. `add` or `set`.
            option_keys: The list of option keys e.g. `loader`, `job`.
        """
        super().__init__(
            CliContextSchema.url,
            {
                "command": command,
                "sub_command": sub_command,
                "option_keys": option_keys or [],
            },
        )

    @classmethod
    def from_command_and_kwargs(
        cls, command: str, sub_command: str | None = None, **kwargs
    ) -> CliContext:
        """Initialize a CLI context.

        Args:
            command: The CLI command.
            sub_command: The CLI sub command.
            kwargs: Additional key-value pairs to evaluate as option_keys if they are not None/False.

        Returns:
            A CLI context.
        """
        return cls(
            command=command,
            sub_command=sub_command,
            option_keys=[key for key, val in kwargs.items() if val],
        )

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> CliContext:
        """Initialize a CLI context.

        Args:
            ctx: The click.Context to derive our invocation args from.

        Returns:
            A CLI context.
        """

        def _recursively_collect_params(crawl_ctx: click.Context) -> dict:
            options = {}
            for key, val in crawl_ctx.params.items():
                if isinstance(val, (bool, int, float)) or val is None:
                    options[key] = val
                else:
                    options[key] = hash_sha256(str(val))
            if crawl_ctx.parent:
                options.update(_recursively_collect_params(crawl_ctx.parent))
            return options

        options = _recursively_collect_params(ctx)

        if ctx.parent and ctx.parent.command.name != "cli":
            return cls(
                command=ctx.parent.command.name,
                sub_command=ctx.command.name,
                options=options,
            )

        return cls(
            command=ctx.command.name,
            sub_command=None,
            options=options,
        )
