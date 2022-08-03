"""Environment management in CLI."""

from __future__ import annotations

import click

from meltano.cli.params import pass_project
from meltano.core.environment_service import EnvironmentService
from meltano.core.project import Project
from meltano.core.tracking import CliEvent

from . import cli
from .utils import InstrumentedGroup, PartialInstrumentedCmd

ENVIRONMENT_SERVICE_KEY = "environment_service"


@cli.group(cls=InstrumentedGroup, name="environment", short_help="Manage environments.")
@click.pass_context
@pass_project(migrate=True)
def meltano_environment(project: Project, ctx: click.Context):
    """
    Manage Environments.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#environment
    """
    ctx.obj[ENVIRONMENT_SERVICE_KEY] = EnvironmentService(project)


@meltano_environment.command(cls=PartialInstrumentedCmd)
@click.argument("name")
@click.pass_context
def add(ctx: click.Context, name: str):
    """Add a new environment."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        environment = environment_service.add(name)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    click.echo(f"Created new environment '{environment.name}'")
    tracker.track_command_event(CliEvent.completed)


@meltano_environment.command(cls=PartialInstrumentedCmd)
@click.argument("name")
@click.pass_context
def remove(ctx: click.Context, name: str):
    """Remove an environment."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        environment_name = environment_service.remove(name)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    click.echo(f"Removed environment '{environment_name}'")
    tracker.track_command_event(CliEvent.completed)


@meltano_environment.command(cls=PartialInstrumentedCmd, name="list")
@click.pass_context
def list_environments(ctx: click.Context):
    """List available environments."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        for environment in environment_service.list_environments():
            click.echo(environment.name)
    except Exception:
        tracker.track_command_event(CliEvent.failed)
        raise
    tracker.track_command_event(CliEvent.completed)
