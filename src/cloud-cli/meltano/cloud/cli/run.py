"""Run a Meltano project in Meltano Cloud."""

from __future__ import annotations

import asyncio
import os

import click

from meltano.cloud.cli.base import cloud
from meltano.cloud.client import MeltanoCloudClient


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
        raise click.UsageError(f"Environment variable {name} is not set.")

    return value


async def run_project(
    api_key: str,
    api_url: str,
    runner_secret: str,
    tenant_resource_key: str,
    project_id: str,
    environment: str,
    job_or_schedule: str,
) -> dict:
    """Run a project in Meltano Cloud.

    Args:
        api_key: The API key to use for authentication.
        api_url: The Meltano Cloud API URL.
        runner_secret: The runner secret to use for authentication.
        tenant_resource_key: The tenant resource key.
        project_id: The project identifier.
        environment: The environment to run in.
        job_or_schedule: The job or schedule identifier.

    Returns:
        The new run details.
    """
    async with MeltanoCloudClient(api_url, api_key, runner_secret) as client:
        return await client.run_project(
            tenant_resource_key,
            project_id,
            environment,
            job_or_schedule,
        )


@cloud.command()
@click.argument("job_or_schedule")
@click.option("--environment", required=True, help="The environment to run in.")
@click.option("--project-id", required=True, help="The project identifier.")
def run(job_or_schedule: str, environment: str, project_id: str) -> None:
    """Run a Meltano project in Meltano Cloud.

    Args:
        job_or_schedule: The job or schedule identifier.
        environment: The environment to run in.
        project_id: The project identifier.
    """
    click.echo("Running a Meltano project in Meltano Cloud.")

    # TODO: This would be different for beta?
    api_url = "https://cloud-runners.meltano.com/v1"

    # TODO: source this properly
    api_key = get_env_var("MELTANO_RUNNER_API_KEY")
    runner_secret = get_env_var("MELTANO_RUNNER_SECRET")
    tenant_resource_key = get_env_var("MELTANO_TENANT_RESOURCE_KEY")

    result = asyncio.run(
        run_project(
            api_key,
            api_url,
            runner_secret,
            tenant_resource_key,
            project_id,
            environment,
            job_or_schedule,
        )
    )
    click.echo(result)
