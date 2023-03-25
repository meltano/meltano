"""Meltano project execution history."""

from __future__ import annotations

import datetime
import json
import typing as t

import click
import tabulate

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudExecution
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

MAX_PAGE_SIZE = 250
UTC = datetime.timezone.utc


async def _get_history(
    config: MeltanoCloudConfig,
    schedule_filter: str | None,
    limit: int,
) -> list[CloudExecution]:
    """Get a Meltano project execution history in Meltano Cloud.

    Args:
        config: The meltano config to use
        schedule_filter: Used to filter the history by schedule name.
        limit: The maximum number of history items to return.

    Returns:
        The execution history.
    """
    page_token = None
    page_size = min(limit, MAX_PAGE_SIZE)
    results: list[CloudExecution] = []

    async with MeltanoCloudClient(config=config) as client:
        while True:
            response = await client.get_execution_history(
                schedule=schedule_filter,
                page_size=page_size,
                page_token=page_token,
            )

            results.extend(response["results"])

            if response["pagination"] and len(results) < limit:
                page_token = response["pagination"]["next_page_token"]
            else:
                break

    return results[:limit]


def process_table_row(row: CloudExecution) -> tuple[str, ...]:
    """Process a table row.

    Args:
        row: The row to process.

    Returns:
        The processed row.
    """
    start_time = datetime.datetime.fromisoformat(row["start_time"])

    if row["end_time"]:
        end_time = datetime.datetime.fromisoformat(row["end_time"])
        td = end_time - start_time
        sec = int(td.total_seconds())
        hours, remainder = divmod(sec, 3600)  # noqa: WPS432
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        duration = "N/A"

    status = (
        "Running"
        if row["status"] not in {"STOPPED", "DELETED"}
        else "Success"
        if row["exit_code"] == 0
        else "Failed"
    )

    return (  # noqa: WPS227
        row["execution_id"],
        row["schedule_name"],
        row["environment_name"],
        start_time.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        status,
        duration,
    )


def _format_history_table(history: list[CloudExecution], table_format: str) -> str:
    """Format the history as a table.

    Args:
        history: The history to format.
        table_format: The table format to use.

    Returns:
        The formatted history.
    """
    return tabulate.tabulate(
        [process_table_row(execution) for execution in history],
        headers=[
            "Execution ID",
            "Schedule Name",
            "Deployment",
            "Executed At (UTC)",
            "Result",
            "Duration",
        ],
        tablefmt=table_format,
    )


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
@pass_context
@run_async
async def history(
    context: MeltanoCloudCLIContext,
    *,
    schedule_filter: str | None,
    limit: int,
    output_format: str,
) -> None:
    """Get a Meltano project execution history in Meltano Cloud."""
    items = await _get_history(
        context.config,
        schedule_filter=schedule_filter,
        limit=limit,
    )

    if output_format == "json":
        output = json.dumps(items, indent=2)
    elif output_format == "markdown":
        output = _format_history_table(items, table_format="github")
    else:
        output = _format_history_table(items, table_format="rounded_outline")

    click.echo(output)
