"""Meltano Cloud CLI."""

from __future__ import annotations

import click
from structlog import get_logger

from meltano.cloud.api import MeltanoCloudError
from meltano.cloud.cli import (
    config,
    deployment,
    docs,  # noqa: WPS235
    history,
    job,
    login,
    logs,
    project,
    run,
    schedule,
    state,
)
from meltano.cloud.cli.base import cloud

logger = get_logger()

cloud.add_command(config.config)
cloud.add_command(docs.docs)
cloud.add_command(deployment.deployment_group)
cloud.add_command(history.history)
cloud.add_command(job.job_group)
cloud.add_command(login.login)
cloud.add_command(login.logout)
cloud.add_command(logs.logs)
cloud.add_command(project.project_group)
cloud.add_command(run.run)
cloud.add_command(schedule.schedule_group)
cloud.add_command(state.state_group)


def main() -> int:
    """Run the Meltano Cloud CLI.

    Returns:
        The CLI exit code.
    """
    try:
        cloud()
    except MeltanoCloudError as e:
        click.secho(e.response.reason, fg="red")
        return 1
    except Exception as e:
        logger.error("An unexpected error occurred.", exc_info=e)
        return 1
    return 0
