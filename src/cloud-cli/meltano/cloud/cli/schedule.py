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
@click.option(
    "--deployment",
    required=True,
    help="The Meltano Cloud deployment the schedule is for.",
)
@click.pass_context
def schedule_group(context: click.Context, deployment: str) -> None:
    """Interact with Meltano Cloud project schedules."""
    context.ensure_object(dict)
    context.obj["deployment"] = deployment


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
        await client.schedule_put_enabled(
            deployment=deployment,
            schedule=schedule,
            enabled=enabled,
        )


@schedule_group.command("enable")
@click.argument("schedule")
@click.pass_context
def enable(context: click.Context, schedule: str) -> None:
    """Enable a Meltano Cloud schedule."""
    asyncio.run(
        set_enabled_state(
            config=context.obj["config"],
            deployment=context.obj["deployment"],
            schedule=schedule,
            enabled=True,
        )
    )


@schedule_group.command("disable")
@click.argument("schedule")
@click.pass_context
def disable(context: click.Context, schedule: str) -> None:
    """Disable a Meltano Cloud schedule."""
    asyncio.run(
        set_enabled_state(
            config=context.obj["config"],
            deployment=context.obj["deployment"],
            schedule=schedule,
            enabled=False,
        )
    )
