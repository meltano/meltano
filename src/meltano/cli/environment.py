"""Environment management in CLI."""

import click

from meltano.cli.params import pass_project
from meltano.core.environment_service import EnvironmentService
from meltano.core.project import Project

from . import cli

ENVIRONMENT_SERVICE_KEY = "environment_service"


@cli.group(name="environment", short_help="Manage environments.")
@click.pass_context
@pass_project(migrate=True)
def meltano_environment(project: Project, ctx: click.Context):
    """
    Manage Environments.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#environment
    """
    ctx.obj[ENVIRONMENT_SERVICE_KEY] = EnvironmentService(project)


@meltano_environment.command()
@click.argument("name")
@click.pass_context
def add(ctx: click.Context, name: str):
    """Add a new environment."""
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    environment = environment_service.add(name)
    click.echo(f"Created new environment '{environment.name}'")


@meltano_environment.command()
@click.argument("name")
@click.pass_context
def remove(ctx: click.Context, name: str):
    """Remove an environment."""
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    environment_name = environment_service.remove(name)
    click.echo(f"Removed environment '{environment_name}'")


@meltano_environment.command(name="list")
@click.pass_context
def list_environments(ctx: click.Context):
    """List available environments."""
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]

    for environment in environment_service.list_environments():
        click.echo(environment.name)
