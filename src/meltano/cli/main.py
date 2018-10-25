import click

from meltano.core.utils import setup_logging
from .params import db_options


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    setup_logging()
