"""Meltano Cloud `schedules` command."""

from __future__ import annotations

import asyncio
import typing as t
from http import HTTPStatus

import click

from meltano.cloud.api.client import MeltanoCloudClient, MeltanoCloudError
from meltano.cloud.cli.base import cloud, pass_context, shared_option

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


class SchedulesCloudClient(MeltanoCloudClient):
    """A Meltano Cloud client with extensions for schedules."""

    async def schedule_put_enabled(
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
                        f"Unable to find schedule named {deployment_name!r} "
                        f"within a deployment named {schedule_name!r}"
                    )
                    raise MeltanoCloudError(ex.response) from ex
                raise


async def set_enabled_state(
    *,
    config: MeltanoCloudConfig,
    deployment_name: str | None,
    schedule_name: str | None,
    enabled: bool,
):
    """Update the enabled state of a Meltano Cloud project schedule.

    Args:
        config: The Meltano Cloud config.
        deployment: The name of the deployment the schedule belongs to.
        schedule: The name of the schedule to enable/disable.
        enabled: Whether the schedule should be enabled.
    """
    if schedule_name is None:
        raise click.UsageError("Missing option '--schedule'")
    if deployment_name is None:
        raise click.UsageError("Missing option '--deployment'")
    async with SchedulesCloudClient(config=config) as client:
        await client.schedule_put_enabled(
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
    help="The name of the schedule.",
)


@cloud.group(name="schedule")
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
        set_enabled_state(
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
        set_enabled_state(
            config=context.config,
            deployment_name=context.deployment,
            schedule_name=context.schedule,
            enabled=False,
        )
    )
