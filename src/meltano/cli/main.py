import click
import logging

from meltano.core.utils import setup_logging
from .params import db_options


LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@click.group(invoke_without_command=True)
@click.option("--log-level", type=click.Choice(LEVELS.keys()), default="info")
@click.pass_context
def cli(ctx, log_level):
    setup_logging(log_level=LEVELS[log_level])
