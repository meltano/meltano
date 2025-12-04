from __future__ import annotations

import difflib
import sys

import click
import click.exceptions
import click.utils

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override


class DYMGroup(click.Group):
    """Provides *Did you mean ...* suggestions when a command is not found."""

    CUTOFF = 0.5
    MAX_SUGGESTIONS = 3

    @override
    def resolve_command(
        self,
        ctx: click.Context,
        args: list[str],
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Resolve a command from a list of commands.

        Appends *Did you mean ...* suggestions to the raised exception message.
        """
        try:
            return super().resolve_command(ctx, args)
        except click.exceptions.UsageError as error:
            error_msg = str(error)

            if matches := difflib.get_close_matches(
                click.utils.make_str(args[0]),
                self.list_commands(ctx),
                n=self.MAX_SUGGESTIONS,
                cutoff=self.CUTOFF,
            ):
                fmt_matches = "\n    ".join(matches)
                error_msg += f"\n\nDid you mean one of these?\n    {fmt_matches}"

            raise click.exceptions.UsageError(error_msg, error.ctx) from None
