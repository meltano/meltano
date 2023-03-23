"""Meltano Cloud CLI."""

from __future__ import annotations

import click
from structlog import get_logger

from meltano.cloud.api import MeltanoCloudError
from meltano.cloud.cli import history, logs, run, schedule
from meltano.cloud.cli.base import cloud

logger = get_logger()


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
