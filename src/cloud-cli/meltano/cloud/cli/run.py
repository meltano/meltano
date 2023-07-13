"""Run a Meltano project in Meltano Cloud."""

from __future__ import annotations

import typing as t

import click

from meltano.cloud.api.client import MeltanoCloudClient
from meltano.cloud.cli.base import pass_context, run_async

if t.TYPE_CHECKING:
    from meltano.cloud.api.config import MeltanoCloudConfig
    from meltano.cloud.cli.base import MeltanoCloudCLIContext


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


@click.command()
@click.argument("job_or_schedule")
@click.option(
    "--deployment",
    help="The name of the Meltano Cloud deployment to run in.",
)
@pass_context
@run_async
async def run(
    context: MeltanoCloudCLIContext,
    job_or_schedule: str,
    deployment: str | None = None,
) -> None:
    """Run a Meltano project in Meltano Cloud."""
    deployment = (
        deployment
        if deployment is not None
        else context.config.internal_project_default["default_deployment_name"]
    )
    if deployment is None:
        raise click.UsageError(
            "A deployment name is required. Please specify "
            "one with the '--deployment' option, or specify a default"
            "deployment by running 'meltano cloud deployment use'.",
        )
    click.echo("Running a Meltano project in Meltano Cloud.")

    result = await run_project(
        deployment,
        job_or_schedule,
        context.config,
    )

    click.echo(result)
