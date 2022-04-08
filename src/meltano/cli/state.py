"""State management in CLI."""
from typing import List, Optional

import click

from meltano.cli.params import pass_project
from meltano.core.project import Project
from meltano.core.state_service import StateService

from . import cli

STATE_SERVICE_KEY = "state_service"


@cli.group(name="state", short_help="Manage Singer state.")
def meltano_state(project: Project, ctx: click.Context):
    """
    Manage state.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#environment
    """
    return  # TODO: ?


@meltano_state.command()
@click.option("--pattern", help="TODO")
def list(ctx: click.Context, pattern: Optional[str]):
    """List all current state for this project."""
    state_service: StateService = ctx.obj[STATE_SERVICE_KEY]
    if pattern:
        states = state_services.list(pattern)
    else:
        states = state_service.list_all()
    for state in states:
        click.echo(state)


@meltano_state.command()
@click.option("--input-file", type=click.Path(exists=True), help="TODO")
@click.argument("state_json_text", help="TODO")
@click.argument("job_id", help="TODO")
def set(
    ctx: click.Context,
    job_id: str,
    state_json_text: Optional[str],
    json_state_file: Optional[click.Path],
):
    """Set state."""
    state_service: StateService = ctx.obj[STATE_SERVICE_KEY]

    if input_file and state_json_text:
        raise ValueError("TODO: better error here")
    elif input_file:
        with open(input_file) as state_f:
            state_service.set(job_id, state_f.read())
    elif state_json_text:
        state_service.set(job_id, state_json_text)
    else:
        raise ValueError("TODO: better error here")


@meltano_state.command()
@click.argument("job_id", help="TODO")
def get(ctx: click.Context, job_id: str):
    """Get state."""
    state_service: StateService = ctx.obj[STATE_SERVICE_KEY]
    click.echo(state_service.get_state(job_id))


@meltano_state.command()
@click.argument("job_id", help="TODO")
def clear(ctx: click.Context, job_id: str):
    """Clear state."""
    state_service: StateService = ctx.obj[STATE_SERVICE_KEY]
    state_service.clear(job_id)
