import click
import logging
import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

import meltano
from meltano.core.project import Project, ProjectNotFound
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
@click.option("-v", "--verbose", count=True)
@click.version_option(version=meltano.__version__, prog_name="meltano")
@click.pass_context
def cli(ctx, log_level, verbose):
    setup_logging(log_level=LEVELS[log_level])
    ctx.ensure_object(dict)
    ctx.obj["verbosity"] = verbose

    try:
        ctx.obj["project"] = Project.find()
    except ProjectNotFound as err:
        ctx.obj["project"] = None
