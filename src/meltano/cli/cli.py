import click
import logging
import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

from meltano.core.project import Project, ProjectNotFound
from meltano.core.utils import setup_logging
from meltano import __version__

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

def print_version(ctx, param, value):
    """
    Print out Meltano version currently in use
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()

@click.group(invoke_without_command=True)
@click.option("--log-level", type=click.Choice(LEVELS.keys()), default="info")
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('--v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.pass_context
def cli(ctx, log_level):
    setup_logging(log_level=LEVELS[log_level])
    ctx.ensure_object(dict)

    try:
        ctx.obj["project"] = Project.find()
    except ProjectNotFound as err:
        ctx.obj["project"] = None
