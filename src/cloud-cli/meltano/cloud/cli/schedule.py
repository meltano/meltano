"""Meltano Cloud `schedules` command."""

from __future__ import annotations

import asyncio
import itertools as it
import json
import typing as t
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import click
import tabulate
from croniter import croniter, croniter_range

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli.base import pass_context, shared_option

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.api.types import CloudProjectSchedule
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

MAX_PAGE_SIZE = 250


class SchedulesCloudClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for schedules."""

    async def set_schedule_enabled(
        self,
        *,
        deployment_name: str,
        schedule_name: str,
        enabled: bool,
    ):
        """Use PUT to update the enabled state of a Meltano Cloud project schedule.

        Args:
            deployment: The name of the deployment the schedule belongs to.
            schedule: The name of the schedule to enable/disable.
            enabled: Whether the schedule should be enabled.

        Raises:
            MeltanoCloudError: The Meltano Cloud API responded with an error.
        """
        async with self.authenticated():
            try:
                await self._json_request(
                    "PUT",
                    "/".join(
                        (
                            "/schedules/v1",
                            f"{self.config.tenant_resource_key}",
                            f"{self.config.internal_project_id}",
                            deployment_name,
                            schedule_name,
                            "enabled",
                        )
                    ),
                    json=enabled,
                )
            except MeltanoCloudError as ex:
                if ex.response.status == HTTPStatus.NOT_FOUND:
                    ex.response.reason = (
                        f"Unable to find schedule named {schedule_name!r} "
                        f"within a deployment named {deployment_name!r}"
                    )
                    raise MeltanoCloudError(ex.response) from ex
                raise

    async def get_schedule(
        self,
        *,
        deployment_name: str,
        schedule_name: str,
    ):
        """Use GET to get a Meltano Cloud project schedule.

        Args:
            deployment_name: The name of the deployment the schedule belongs to.
            schedule_name: The name of the schedule.

        Raises:
            MeltanoCloudError: The Meltano Cloud API responded with an error.
        """
        async with self.authenticated():
            try:
                return await self._json_request(
                    "GET",
                    "/".join(
                        (
                            "/schedules/v1",
                            self.config.tenant_resource_key,
                            self.config.internal_project_id,
                            deployment_name,
                            schedule_name,
                        )
                    ),
                )
            except MeltanoCloudError as ex:
                if ex.response.status == HTTPStatus.NOT_FOUND:
                    ex.response.reason = (
                        f"Unable to find schedule named {schedule_name!r} "
                        f"within a deployment named {deployment_name!r}"
                    )
                    raise MeltanoCloudError(ex.response) from ex
                raise

    async def get_schedules(
        self,
        *,
        deployment_name: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """Use GET to get Meltano Cloud project schedules.

        Args:
            deployment_name: The name of the deployment the schedule belongs to.
            page_size: The number of items to request per page.
            page_token: The page token.

        Raises:
            MeltanoCloudError: The Meltano Cloud API responded with an error.
        """
        params: dict[str, t.Any] = {
            "page_size": page_size,
            "page_token": page_token,
        }

        path = [
            "/schedules/v1",
            self.config.tenant_resource_key,
            self.config.internal_project_id,
        ]
        if deployment_name is not None:
            path.append(deployment_name)

        async with self.authenticated():
            return await self._json_request(
                "GET", "/".join(path), params=self.clean_params(params)
            )


async def _set_enabled_state(
    *,
    config: MeltanoCloudConfig,
    deployment_name: str | None,
    schedule_name: str | None,
    enabled: bool,
):
    if schedule_name is None:
        raise click.UsageError("Missing option '--schedule'")
    if deployment_name is None:
        raise click.UsageError("Missing option '--deployment'")
    async with SchedulesCloudClient(config=config) as client:
        await client.set_schedule_enabled(
            deployment_name=deployment_name,
            schedule_name=schedule_name,
            enabled=enabled,
        )


deployment_option = shared_option(
    "--deployment",
    help="The name of the Meltano Cloud deployment the schedule belongs to.",
)

schedule_option = shared_option(
    "--schedule",
    help="The name of a schedule within the specified deployment.",
)


@click.group("schedule")
@deployment_option
@schedule_option
def schedule_group() -> None:
    """Interact with Meltano Cloud project schedules."""


@schedule_group.command("enable")
@deployment_option
@schedule_option
@pass_context
def enable(context: MeltanoCloudCLIContext) -> None:
    """Enable a Meltano Cloud schedule."""
    asyncio.run(
        _set_enabled_state(
            config=context.config,
            deployment_name=context.deployment,
            schedule_name=context.schedule,
            enabled=True,
        )
    )


@schedule_group.command("disable")
@deployment_option
@schedule_option
@pass_context
def disable(context: MeltanoCloudCLIContext) -> None:
    """Disable a Meltano Cloud schedule."""
    asyncio.run(
        _set_enabled_state(
            config=context.config,
            deployment_name=context.deployment,
            schedule_name=context.schedule,
            enabled=False,
        )
    )


async def _get_schedule(
    config: MeltanoCloudConfig,
    deployment_name: str | None,
    schedule_name: str | None,
) -> CloudProjectSchedule:
    if schedule_name is None:
        raise click.UsageError("Missing option '--schedule'")
    if deployment_name is None:
        raise click.UsageError("Missing option '--deployment'")
    async with SchedulesCloudClient(config=config) as client:
        return await client.get_schedule(
            deployment_name=deployment_name, schedule_name=schedule_name
        )


async def _get_schedules(
    config: MeltanoCloudConfig,
    deployment_name: str | None,
    limit: int,
) -> list[CloudProjectSchedule]:
    page_token = None
    page_size = min(limit, MAX_PAGE_SIZE)
    results: list[CloudProjectSchedule] = []

    async with SchedulesCloudClient(config=config) as client:
        while True:
            response = await client.get_schedules(
                deployment_name=deployment_name,
                page_size=page_size,
                page_token=page_token,
            )

            results.extend(response["results"])

            if response["pagination"] and len(results) < limit:
                page_token = response["pagination"]["next_page_token"]
            else:
                break

    return results[:limit]


def _next_n_runs(n: int, cron_expr: str) -> tuple[datetime, ...]:
    now = datetime.now(timezone.utc)
    return tuple(it.islice(croniter(cron_expr, now, ret_type=datetime), n))


def _approx_daily_freq(cron_expr: str) -> float:
    now = datetime.now(timezone.utc)
    num_days = 365
    num_runs = sum(1 for _ in croniter_range(now, now + timedelta(num_days), cron_expr))
    return num_runs / num_days


def _process_table_row(schedule: CloudProjectSchedule) -> tuple[str | float, ...]:
    return (
        schedule["deployment_name"],
        schedule["schedule_name"],
        schedule["interval"],
        _approx_daily_freq(schedule["interval"]),
        schedule["enabled"],
    )


def _format_schedules_table(
    schedules: list[CloudProjectSchedule], table_format: str
) -> str:
    """Format the schedules as a table.

    Args:
        schedules: The schedules to format.

    Returns:
        The formatted schedules.
    """
    return tabulate.tabulate(
        [_process_table_row(schedule) for schedule in schedules],
        headers=(
            "Deployment",
            "Schedule",
            "Interval",
            "Runs / Day",
            "Enabled",
        ),
        tablefmt=table_format,
        floatfmt=".3f",
    )


schedule_list_formatters = {
    "json": lambda schedules: json.dumps(schedules, indent=2),
    "markdown": lambda schedules: _format_schedules_table(
        schedules, table_format="github"
    ),
    "terminal": lambda schedules: _format_schedules_table(
        schedules, table_format="rounded_outline"
    ),
}


@schedule_group.command("list")
@deployment_option
@click.option(
    "--limit",
    required=False,
    type=int,
    default=10,
    help="The maximum number of schedules to display.",
)
@click.option(
    "--format",
    "output_format",
    required=False,
    default="terminal",
    type=click.Choice(("terminal", "markdown", "json")),
    help="The output format to use.",
)
@pass_context
def list_schedules(
    context: MeltanoCloudCLIContext,
    output_format: str | None,
    limit: int,
) -> None:
    """List Meltano Cloud schedules."""
    click.echo(
        schedule_list_formatters[output_format](
            asyncio.run(
                _get_schedules(
                    config=context.config,
                    deployment_name=context.deployment,
                    limit=limit,
                ),
            )
        )
    )


@schedule_group.command("describe")
@deployment_option
@schedule_option
@pass_context
def describe_schedule(context: MeltanoCloudCLIContext) -> None:
    """List Meltano Cloud schedules."""
    schedule = asyncio.run(
        _get_schedule(
            config=context.config,
            deployment_name=context.deployment,
            schedule_name=context.schedule,
        ),
    )
    click.echo(
        f"Deployment name: {schedule['deployment_name']}\n"
        f"Schedule name:   {schedule['schedule_name']}\n"
        f"Interval:        {schedule['interval']}\n"
        f"Enabled:         {schedule['enabled']}"
    )
    if schedule["enabled"]:
        click.echo(
            "\nApproximate starting date and time (UTC) of next 5 schedule runs:"
        )
        for dt in _next_n_runs(5, schedule["interval"]):
            click.echo(dt.strftime("%Y-%m-%d %H:%M"))
