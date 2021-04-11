import click

from . import cli
from .params import pass_project


@cli.command()
@pass_project()
@click.pass_context
def remove(ctx, project):
    """Remove a plugin from your project."""
