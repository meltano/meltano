"""Run a Meltano project in Meltano Cloud."""

from __future__ import annotations

import asyncio
import typing as t

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import cloud

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig


async def run_project(
    deployment: str,
    job_or_schedule: str,
    config: MeltanoCloudConfig,
) -> dict | str:
    """Run a project in Meltano Cloud.

    Args:
        deployment: The name of the Meltano Cloud deployment to run in.
        job_or_schedule: The name of the job or schedule to run.
        config: the meltano config to use

    Returns:
        The new run details.
    """
    async with MeltanoCloudClient(config=config) as client:
        return await client.run_project(
            deployment,
            job_or_schedule,
        )


@cloud.command()
@click.argument("job_or_schedule")
@click.option(
    "--deployment",
    required=True,
    help="The name of the Meltano Cloud deployment to run in.",
)
@click.pass_context
def run(
    ctx: click.Context,
    job_or_schedule: str,
    deployment: str,
) -> None:
    """Run a Meltano project in Meltano Cloud."""
    click.echo("Running a Meltano project in Meltano Cloud.")

    result = asyncio.run(
        run_project(
            deployment,
            job_or_schedule,
            ctx.obj["config"],
        ),
    )
    click.echo(result)
