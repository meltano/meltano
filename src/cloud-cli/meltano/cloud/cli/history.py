"""Meltano project execution history."""

from __future__ import annotations

import asyncio
import datetime
import json
import typing as t

import click
import tabulate

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import cloud

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudExecution

MAX_PAGE_SIZE = 250


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


def _format_history_table(history: list[CloudExecution]) -> str:
    """Format the history as a table.

    Args:
        history: The history to format.

    Returns:
        The formatted history.
    """
    table = []
    headers = ["Execution ID", "Schedule Name", "Executed At", "Result", "Duration"]

    for execution in history:
        start_time = datetime.datetime.fromisoformat(execution["start_time"])

        if execution["end_time"]:
            end_time = datetime.datetime.fromisoformat(execution["end_time"])
            td = end_time - start_time
            sec = int(td.total_seconds())
            hours, remainder = divmod(sec, 3600)  # noqa: WPS432
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            duration = "N/A"

        table.append(
            [
                execution["execution_id"],
                execution["schedule_name"],
                execution["start_time"],
                "Success" if execution["exit_code"] == 0 else "Failed",
                duration,
            ],
        )

    return tabulate.tabulate(table, headers, tablefmt="github")


@cloud.command()
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
    default="table",
    type=click.Choice(["table", "json"]),
    help="The output format to use.",
)
@click.pass_context
def history(
    ctx: click.Context,
    *,
    schedule_filter: str | None,
    limit: int,
    output_format: str,
) -> None:
    """Get a Meltano project execution history in Meltano Cloud."""
    items = asyncio.run(
        _get_history(
            ctx.obj["config"],
            schedule_filter=schedule_filter,
            limit=limit,
        ),
    )

    if output_format == "json":
        output = json.dumps(items, indent=2)
    else:
        output = _format_history_table(items)

    click.echo(output)
