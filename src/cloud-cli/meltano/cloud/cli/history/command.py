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
        param: click.Parameter | None,  # noqa: ARG002
        ctx: click.Context | None,  # noqa: ARG002
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


def _arg_to_glob_filter(
    schedule: str | None,
    schedule_prefix: str | None,
    schedule_contains: str | None,
) -> str | None:
    """Convert the schedule filter arguments to a glog expression.

    Args:
        schedule: The schedule name to match.
        schedule_prefix: The schedule name prefix to match.
        schedule_contains: The schedule name substring to match.

    Returns:
        The glog expression to use for filtering.

    Raises:
        click.UsageError: More than one filter was specified.
    """
    # If more than one filter is specified, fail.
    if sum(1 for f in (schedule, schedule_prefix, schedule_contains) if f) > 1:
        raise click.UsageError(
            "Only one of --schedule, --schedule-prefix, or "
            "--schedule-contains can be specified.",
        )

    if schedule:
        return schedule

    if schedule_prefix:
        return f"{schedule_prefix}*"

    if schedule_contains:
        return f"*{schedule_contains}*"

    return None


@click.command()
@click.option(
    "--schedule",
    required=False,
    help="Match schedules by this exact name.",
)
@click.option(
    "--schedule-prefix",
    required=False,
    help="Match schedules that start with the specified string.",
)
@click.option(
    "--schedule-contains",
    "--filter",
    "schedule_contains",
    required=False,
    help="Match schedules that contain the specified string.",
)
@click.option(
    "--deployment",
    required=False,
    help="Match deployments by this exact name.",
)
@click.option(
    "--deployment-prefix",
    required=False,
    help="Match deployments that start with the specified string.",
)
@click.option(
    "--deployment-contains",
    required=False,
    help="Match deployments that contain the specified string.",
)
@click.option(
    "--result",
    required=False,
    type=click.Choice(["success", "failed", "running"]),
    help="Match executions by result.",
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
    schedule: str | None,
    schedule_prefix: str | None,
    schedule_contains: str | None,
    deployment: str | None,
    deployment_prefix: str | None,
    deployment_contains: str | None,
    result: str | None,
    limit: int,
    output_format: str,
    lookback: datetime.timedelta | None,
) -> None:
    """Get a Meltano project execution history in Meltano Cloud."""
    schedule_filter = _arg_to_glob_filter(
        schedule,
        schedule_prefix,
        schedule_contains,
    )
    deployment_filter = _arg_to_glob_filter(
        deployment,
        deployment_prefix,
        deployment_contains,
    )

    now = datetime.datetime.now(tz=utils.UTC)
    items = await HistoryClient.get_history_list(
        context.config,
        schedule_filter=schedule_filter,
        deployment_filter=deployment_filter,
        result_filter=result,
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
