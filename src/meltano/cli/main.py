import click

from meltano.support.utils import setup_logging
from .params import db_options



@click.group()
def cli():
    setup_logging()
