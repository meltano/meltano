import click
import logging
import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

from meltano.core.utils import setup_logging


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
