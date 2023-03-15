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
    try:
        return os.environ[name]
    except KeyError:
        msg = f"Environment variable {name} is not set."
        raise click.UsageError(msg)


async def run_project(
    organization_id: str,
    project_id: str,
    deployment: str,
    job_or_schedule: str,
    config: MeltanoCloudConfig,
) -> dict | str:
    """Run a project in Meltano Cloud.

    Args:
        organization_id: The Meltano Cloud Organization ID.
        project_id: The Meltano Cloud project ID.
        deployment: The name of the Meltano Cloud deployment to run in.
        job_or_schedule: The name of the job or schedule to run.
        config: the meltano config to use

    Returns:
        The new run details.
    """
    async with MeltanoCloudClient(config=config) as client:
        return await client.run_project(
            organization_id,
            project_id,
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
@click.option("--project-id", required=True, help="The Meltano Cloud project ID.")
@click.pass_context
def run(
    ctx: click.Context,
    job_or_schedule: str,
    deployment: str,
    project_id: str,
) -> None:
    """Run a Meltano project in Meltano Cloud."""
    click.echo("Running a Meltano project in Meltano Cloud.")
    organization_id = get_env_var("MELTANO_CLOUD_ORGANIZATION_ID")

    result = asyncio.run(
        run_project(
            organization_id,
            project_id,
            deployment,
            job_or_schedule,
            ctx.obj["config"],
        ),
    )
    click.echo(result)
