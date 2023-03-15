"""Meltano Cloud `schedules` command."""

from __future__ import annotations

import asyncio
import typing as t

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import cloud

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig


@cloud.group(name="schedule")
def schedule_group() -> None:
    """Interact with Meltano Cloud project schedules."""


async def set_enabled_state(
    *,
    config: MeltanoCloudConfig,
    deployment: str,
    schedule: str,
    enabled: bool,
):
    """Update the enabled state of a Meltano Cloud project schedule.

    Args:
        config: The Meltano Cloud config.
        deployment: The name of the deployment the schedule belongs to.
        schedule: The name of the schedule to enable/disable.
        enabled: Whether the schedule should be enabled.
    """
    async with MeltanoCloudClient(config=config) as client:
        await client.schedule_put_enabled(deployment, schedule, enabled)


deployment_option = click.option(
    "--deployment",
    required=True,
    help="The Meltano Cloud deployment the schedule is for.",
)


@schedule_group.command("enable")
@deployment_option
@click.argument("schedule")
@click.pass_context
def enable(context: click.Context, deployment: str, schedule: str) -> None:
    """Enable a Meltano Cloud schedule."""
    config: MeltanoCloudConfig = context.obj["config"]
    asyncio.run(
        set_enabled_state(
            config=config,
            deployment=deployment,
            schedule=schedule,
            enabled=True,
        )
    )


@schedule_group.command("disable")
@deployment_option
@click.argument("schedule")
@click.pass_context
def disable(context: click.Context, deployment: str, schedule: str) -> None:
    """Disable a Meltano Cloud schedule."""
    config: MeltanoCloudConfig = context.obj["config"]
    asyncio.run(
        set_enabled_state(
            config=config,
            deployment=deployment,
            schedule=schedule,
            enabled=False,
        )
    )
