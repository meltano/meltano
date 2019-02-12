import click
from . import cli
from meltano import __version__


@cli.command()
def version():
    click.echo(__version__)
