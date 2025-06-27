"""Environment management in CLI."""

from __future__ import annotations

import typing as t

import click

from meltano.cli.params import pass_project
from meltano.cli.utils import InstrumentedGroup, PartialInstrumentedCmd
from meltano.core.environment_service import EnvironmentService
from meltano.core.tracking.contexts import CliEvent

if t.TYPE_CHECKING:
    from meltano.core.project import Project

ENVIRONMENT_SERVICE_KEY = "environment_service"


@click.group(
    cls=InstrumentedGroup,
    name="environment",
    short_help="Manage environments.",
)
@click.pass_context
@pass_project(migrate=True)
def meltano_environment(project: Project, ctx: click.Context) -> None:
    """Manage Environments.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#environment
    """  # noqa: D301
    ctx.obj[ENVIRONMENT_SERVICE_KEY] = EnvironmentService(project)


@meltano_environment.command(cls=PartialInstrumentedCmd)
@click.argument("name")
@click.pass_context
def add(ctx: click.Context, name: str) -> None:
    """Add a new environment."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        environment = environment_service.add(name)
    except Exception:  # pragma: no cover
        tracker.track_command_event(CliEvent.failed)
        raise
    click.echo(f"Created new environment '{environment.name}'")
    tracker.track_command_event(CliEvent.completed)


@meltano_environment.command(cls=PartialInstrumentedCmd)
@click.argument("name")
@click.pass_context
def remove(ctx: click.Context, name: str) -> None:
    """Remove an environment."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        environment_name = environment_service.remove(name)
    except Exception:  # pragma: no cover
        tracker.track_command_event(CliEvent.failed)
        raise
    click.echo(f"Removed environment '{environment_name}'")
    tracker.track_command_event(CliEvent.completed)


@meltano_environment.command(cls=PartialInstrumentedCmd, name="list")
@click.pass_context
def list_environments(ctx: click.Context) -> None:
    """List available environments."""
    tracker = ctx.obj["tracker"]
    environment_service: EnvironmentService = ctx.obj[ENVIRONMENT_SERVICE_KEY]
    try:
        for environment in environment_service.list_environments():
            click.echo(environment.name)
    except Exception:  # pragma: no cover
        tracker.track_command_event(CliEvent.failed)
        raise
    tracker.track_command_event(CliEvent.completed)
