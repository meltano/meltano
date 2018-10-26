import click
import warnings

# disable the psycopg2 warning
# this needs to run before `psycopg2` is imported
warnings.filterwarnings("ignore", category=UserWarning, module="psycopg2")

from meltano.core.utils import setup_logging


@click.group()
@click.pass_context
def cli(ctx):
    setup_logging()
