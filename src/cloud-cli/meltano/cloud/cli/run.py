"""Run a Meltano project in Meltano Cloud."""

from __future__ import annotations

import asyncio
import os

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.api.config import MeltanoCloudConfig
from meltano.cloud.cli.base import cloud


def get_env_var(name: str) -> str:
    """Expect an environment variable to be set.

    Args:
        name: The environment variable name.

    Returns:
        The environment variable value.

    Raises:
        UsageError: If the environment variable is not set.
    """
    value = os.getenv(name)
    if not value:
        msg = f"Environment variable {name} is not set."
        raise click.UsageError(msg)

    return value


async def run_project(
    organization_id: str,
    project_id: str,
    environment: str,
    job_or_schedule: str,
    config: MeltanoCloudConfig,
) -> dict | str:
    """Run a project in Meltano Cloud.

    Args:
        organization_id: The organization ID.
        project_id: The project identifier.
        environment: The environment to run in.
        job_or_schedule: The job or schedule identifier.
        config: the meltano config to use

    Returns:
        The new run details.
    """
    async with MeltanoCloudClient(config=config) as client:
        return await client.run_project(
            organization_id,
            project_id,
            environment,
            job_or_schedule,
        )


@cloud.command()
@click.argument("job_or_schedule")
@click.option("--environment", required=True, help="The environment to run in.")
@click.option("--project-id", required=True, help="The project identifier.")
@click.pass_context
def run(
    ctx: click.Context,
    job_or_schedule: str,
    environment: str,
    project_id: str,
) -> None:
    """Run a Meltano project in Meltano Cloud."""
    click.echo("Running a Meltano project in Meltano Cloud.")
    organization_id = get_env_var("MELTANO_CLOUD_ORGANIZATION_ID")

    result = asyncio.run(
        run_project(
            organization_id, project_id, environment, job_or_schedule, ctx.obj["config"]
        ),
    )
    click.echo(result)
