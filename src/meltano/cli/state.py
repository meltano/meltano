"""State management in CLI."""
import re
from typing import List, Optional

import click
import structlog

from meltano.cli.params import pass_project
from meltano.core.block.parser import BlockParser
from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.state_service import StateService

from . import cli
from .params import pass_project

STATE_SERVICE_KEY = "state_service"

logger = structlog.getLogger(__name__)


def state_service_from_job_id(project: Project, job_id: str) -> StateService:
    """Instantiate by parsing a job_id"""
    job_id_re = re.compile(r"^(?P<env>.+)\:(?P<tap>.+)-to-(?P<target>.+)$")
    match = job_id_re.match(job_id)
    if not match:
        raise ValueError  # TODO: better error
    if (
        not project.active_environment
    ) or project.active_environment.name != match.group("env"):
        logger.warn("Environment for job does not match current environment.")
        project.activate_environment(match.group("env"))
        print(project.active_environment.name)
    blocks = [match.group("tap"), match.group("target")]
    parser = BlockParser(logger, project, blocks)
    return next(parser.find_blocks()).state_service


@cli.group(name="state", short_help="Manage Singer state.")
@click.pass_context
@pass_project(migrate=True)
def meltano_state(project: Project, ctx: click.Context):
    """
    Manage state.

    \b\nRead more at https://docs.meltano.com/reference/command-line-interface#state
    """
    _, sessionmaker = project_engine(project)
    session = sessionmaker()
    ctx.obj[STATE_SERVICE_KEY] = StateService(session)


@meltano_state.command()
@click.option("--pattern", help="TODO")
@click.pass_context
def list(ctx: click.Context, pattern: Optional[str]):
    """List all job_ids for this project."""
    state_service = ctx.obj[STATE_SERVICE_KEY]
    states = state_service.list_state()
    for job_id, state in states.items():
        if state:
            if "error" in state:
                click.secho(job_id, fg="red")
            else:
                click.secho(job_id, fg="green")
        else:
            click.secho(job_id, fg="yellow")


@meltano_state.command()
@click.option("--input-file", type=click.Path(exists=True), help="TODO")
@click.argument("state_json_text")
@click.argument("job_id")
@click.pass_context
def set(
    ctx: click.Context,
    job_id: str,
    state_json_text: Optional[str],
    json_state_file: Optional[click.Path],
):
    """Set state."""
    state_service = ctx.obj[STATE_SERVICE_KEY]

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
@click.argument("job_id")
@click.pass_context
def get(ctx: click.Context, job_id: str):
    """Get state."""
    state_service = ctx.obj[STATE_SERVICE_KEY]
    click.echo(state_service.get_state(job_id))


@meltano_state.command()
@click.argument("job_id")
@click.pass_context
def clear(ctx: click.Context, job_id: str):
    """Clear state."""
    state_service = ctx.obj[STATE_SERVICE_KEY]
    state_service.clear(job_id)
