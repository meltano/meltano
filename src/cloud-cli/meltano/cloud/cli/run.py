"""Run a Meltano project in Meltano Cloud."""

from __future__ import annotations

import asyncio

import click

from meltano.cloud.cli.base import cloud
from meltano.cloud.client import MeltanoCloudClient


async def run_project(
    api_key: str,
    api_url: str,
    project_id: str,
    job_or_schedule: str,
) -> dict:
    """Run a project in Meltano Cloud.

    Args:
        api_key: The API key to use for authentication.
        api_url: The Meltano Cloud API URL.
        project_id: The project identifier.
        job_or_schedule: The job or schedule identifier.

    Returns:
        The new run details.
    """
    async with MeltanoCloudClient(api_url, api_key) as client:
        return await client.run_project(project_id, job_or_schedule)


@cloud.command()
@click.argument("job_or_schedule")
def run(job_or_schedule: str) -> None:
    """Run a Meltano project in Meltano Cloud.

    Args:
        job_or_schedule: The job or schedule identifier.
    """
    click.echo("Running a Meltano project in Meltano Cloud.")

    # TODO: Retrieve credentials from context.
    api_url = "https://api.meltano.com"
    api_key = "TODO: Get API key from context."

    # TODO: Get project identifier from context.
    project_id = "my-meltano-project"

    # TODO: Request a run from the Meltano Cloud API.
    result = asyncio.run(run_project(api_key, api_url, project_id, job_or_schedule))
    click.echo(result)
