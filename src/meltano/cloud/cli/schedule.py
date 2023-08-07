"""Meltano Cloud `schedules` command."""

from __future__ import annotations

import itertools as it
import typing as t
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import click
from croniter import croniter, croniter_range

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli.base import (
    LimitedResult,
    get_paginated,
    pass_context,
    print_formatted_list,
    shared_option,
)
from meltano.core.utils import run_async

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
                        ),
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
                        ),
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
        deployment_name: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """Use GET to get Meltano Cloud project schedules.

        Args:
            deployment_name: The name of the deployment the schedule belongs to.
            page_size: The number of items to request per page.
            page_token: The page token.
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
                "GET",
                "/".join(path),
                params=self.clean_params(params),
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
    deployment_name = (
        deployment_name
        if deployment_name is not None
        else config.internal_project_default["default_deployment_name"]
    )
    if deployment_name is None:
        raise click.UsageError(
            "A deployment name is required. Please specify "
            "one with the '--deployment' option, or specify a default"
            "deployment by running 'meltano cloud deployment use'.",
        )
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
@run_async
async def enable(context: MeltanoCloudCLIContext) -> None:
    """Enable a Meltano Cloud schedule."""
    await _set_enabled_state(
        config=context.config,
        deployment_name=context.deployment,
        schedule_name=context.schedule,
        enabled=True,
    )


@schedule_group.command("disable")
@deployment_option
@schedule_option
@pass_context
@run_async
async def disable(context: MeltanoCloudCLIContext) -> None:
    """Disable a Meltano Cloud schedule."""
    await _set_enabled_state(
        config=context.config,
        deployment_name=context.deployment,
        schedule_name=context.schedule,
        enabled=False,
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
            deployment_name=deployment_name,
            schedule_name=schedule_name,
        )


async def _get_schedules(
    config: MeltanoCloudConfig,
    deployment_name: str | None,
    limit: int,
) -> LimitedResult[CloudProjectSchedule]:
    async with SchedulesCloudClient(config=config) as client:
        return await get_paginated(
            lambda page_size, page_token: client.get_schedules(
                deployment_name=deployment_name,
                page_size=page_size,
                page_token=page_token,
            ),
            limit,
            MAX_PAGE_SIZE,
        )


def _next_n_runs(n: int, cron_expr: str) -> tuple[datetime, ...]:
    now = datetime.now(timezone.utc)
    return tuple(it.islice(croniter(cron_expr, now, ret_type=datetime), n))


timedelta_year = timedelta(days=365)  # noqa: WPS432


def _approx_daily_freq(
    cron_expr: str,
    sample_period: timedelta = timedelta_year,
    num_digits_precision: int = 1,
) -> str:
    if cron_expr in {"@once", "@manual", "@none"}:
        return "0"
    now = datetime.now(timezone.utc)
    num_runs = sum(1 for _ in croniter_range(now, now + sample_period, cron_expr))
    freq = round(num_runs / sample_period.days, num_digits_precision)
    return "< 1" if freq < 1 else str(freq)


def _format_schedule(
    schedule: CloudProjectSchedule,
) -> tuple[str, str, str, str, bool]:
    return (
        schedule["deployment_name"],
        schedule["schedule_name"],
        schedule["interval"],
        _approx_daily_freq(schedule["interval"]),
        schedule["enabled"],
    )


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
@run_async
async def list_schedules(
    context: MeltanoCloudCLIContext,
    output_format: str,
    limit: int,
) -> None:
    """List Meltano Cloud schedules."""
    results = await _get_schedules(
        config=context.config,
        deployment_name=context.deployment,
        limit=limit,
    )
    print_formatted_list(
        results,
        output_format,
        _format_schedule,
        ("Deployment", "Schedule", "Interval", "Runs / Day", "Enabled"),
        ("left", "left", "left", "right", "left"),
    )


@schedule_group.command("describe")
@deployment_option
@schedule_option
@click.option(
    "--only-upcoming",
    is_flag=True,
    help="Only list upcoming scheduled run start datetimes",
)
@click.option(
    "--num-upcoming",
    type=int,
    default=10,
    help="The number of upcoming scheduled run start datetimes to list",
)
@pass_context
@run_async
async def describe_schedule(
    context: MeltanoCloudCLIContext,
    only_upcoming: bool,
    num_upcoming: int,
) -> None:
    """Describe a Meltano Cloud schedules & list upcoming scheduled runs."""
    schedule = await _get_schedule(
        config=context.config,
        deployment_name=context.deployment,
        schedule_name=context.schedule,
    )

    if not only_upcoming:
        click.echo(
            f"Deployment name: {schedule['deployment_name']}\n"
            f"Schedule name:   {schedule['schedule_name']}\n"
            f"Interval:        {schedule['interval']}\n"
            f"Enabled:         {schedule['enabled']}",
        )
        if schedule["enabled"]:
            click.echo(
                "\nApproximate starting date and time (UTC) of "
                f"next {num_upcoming} scheduled runs:",
            )
    if schedule["enabled"]:
        for dt in _next_n_runs(num_upcoming, schedule["interval"]):
            click.echo(dt.strftime("%Y-%m-%d %H:%M"))
