"""Meltano Cloud history command."""

from __future__ import annotations

import datetime
import json
import typing as t

import click

from meltano.cloud.cli.base import pass_context, run_async
from meltano.cloud.cli.history import utils
from meltano.cloud.cli.history.client import HistoryClient

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


class LookbackExpressionType(click.ParamType):
    """A lookback expression type.

    Examples:
        1w2d3h4m
        1w2d3h
        1w2d
        1w
    """

    name = "lookback"

    def convert(
        self,
        value: str | datetime.timedelta,
        param: click.Parameter | None,
        ctx: click.Context | None,
    ) -> datetime.timedelta:
        """Convert the lookback expression to a timedelta."""
        if isinstance(value, datetime.timedelta):
            return value

        if isinstance(value, str):
            try:
                return utils.lookback_to_interval(value)
            except ValueError:
                self.fail(f"Invalid lookback expression: {value}")

        return value


@click.command()
@click.option(
    "--filter",
    "schedule_filter",
    required=False,
    help="The name or part of the name of a schedule to filter by.",
)
@click.option(
    "--limit",
    required=False,
    type=int,
    default=10,
    help="The maximum number of history items to display.",
)
@click.option(
    "--format",
    "output_format",
    required=False,
    default="terminal",
    type=click.Choice(["terminal", "markdown", "json"]),
    help="The output format to use.",
)
@click.option(
    "--lookback",
    required=False,
    type=LookbackExpressionType(),
    help=(
        "The lookback period to retrieve history for. The format is a "
        "sequence of pairs of a number and a time unit. The supported "
        "units of time time are w (weeks), d (days), h (hours), and m (minutes). "
        "For example: 1w2d3h4m."
    ),
)
@pass_context
@run_async
async def history(
    context: MeltanoCloudCLIContext,
    *,
    schedule_filter: str | None,
    limit: int,
    output_format: str,
    lookback: datetime.timedelta | None,
) -> None:
    """Get a Meltano project execution history in Meltano Cloud."""
    now = datetime.datetime.now(tz=utils.UTC)
    items = await HistoryClient.get_history_list(
        context.config,
        schedule_filter=schedule_filter,
        limit=limit,
        start_time=now - lookback if lookback else None,
    )

    if output_format == "json":
        output = json.dumps(items, indent=2)
    elif output_format == "markdown":
        output = utils.format_history_table(items, table_format="github")
    else:
        output = utils.format_history_table(items, table_format="rounded_outline")

    click.echo(output)
