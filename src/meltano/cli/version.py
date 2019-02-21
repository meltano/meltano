import click
from . import cli
from meltano import __version__


@cli.command()
def version():
    """
    Print out Meltano version currently in use
    """
    click.echo(__version__)
