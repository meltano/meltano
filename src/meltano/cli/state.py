"""State management in CLI."""
import json
import re
from typing import Optional

import click
import structlog

from meltano.cli.params import pass_project
from meltano.core.block.parser import BlockParser
from meltano.core.db import project_engine
from meltano.core.project import Project
from meltano.core.state_service import InvalidJobStateError, StateService

from . import cli

STATE_SERVICE_KEY = "state_service"

logger = structlog.getLogger(__name__)


def state_service_from_job_id(project: Project, job_id: str) -> Optional[StateService]:
    """Instantiate by parsing a job_id."""
    job_id_re = re.compile(r"^(?P<env>.+)\:(?P<tap>.+)-to-(?P<target>.+)$")
    match = job_id_re.match(job_id)
    if match:
        # If the job_id matches convention (i.e., job has been run via "meltano run"),
        # try parsing into BlockSet.
        # This way, we get BlockSet validation and raise an error if no
        # plugin in the BlockSet has "state" capability
        try:
            if (
                not project.active_environment
            ) or project.active_environment.name != match.group("env"):
                logger.warn("Environment for job does not match current environment.")
            project.activate_environment(match.group("env"))
            blocks = [match.group("tap"), match.group("target")]
            parser = BlockParser(logger, project, blocks)
            return next(parser.find_blocks()).state_service
        except Exception:
            logger.warn("No plugins found for provided job_id.")
    # If provided job_id does not match convention (i.e., run via "meltano elt"),
    # use the standalone StateService in the CLI context.
    return None


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


@meltano_state.command(name="list")
@click.option("--pattern", help="TODO")
@click.pass_context
def list_state(ctx: click.Context, pattern: Optional[str]):  # noqa: WPS125
    """List all job_ids for this project."""
    state_service = ctx.obj[STATE_SERVICE_KEY]
    states = state_service.list_state(pattern)

    for job_id, state in states.items():
        if state:
            try:
                state_service.validate_state(json.dumps(state))
            except (InvalidJobStateError, json.decoder.JSONDecodeError):
                click.secho(job_id, fg="red")
            else:
                click.secho(job_id, fg="green")
        else:
            click.secho(job_id, fg="yellow")


@meltano_state.command(name="add")
@click.option("--input-file", type=click.Path(exists=True), help="TODO")
@click.option("--state", type=str, help="TODO")
@click.argument("job_id")
@pass_project(migrate=True)
@click.pass_context
def add_state(
    ctx: click.Context,
    project: Project,
    job_id: str,
    state: Optional[str],
    input_file: Optional[click.Path],
):
    """Add bookmarks to existing state."""
    state_service = (
        state_service_from_job_id(project, job_id) or ctx.obj[STATE_SERVICE_KEY]
    )

    if input_file and state:
        raise ValueError("TODO: better error here")
    elif input_file:
        with open(input_file) as state_f:
            state_service.add_state(job_id, state_f.read())
    elif state:
        state_service.add_state(job_id, state)
    else:
        raise ValueError("TODO: better error here")


@meltano_state.command(name="set")
@click.option("--input-file", type=click.Path(exists=True), help="TODO")
@click.option("--state", type=str, help="TODO")
@click.argument("job_id")
@pass_project(migrate=True)
@click.pass_context
def set_state(
    ctx: click.Context,
    project: Project,
    job_id: str,
    state: Optional[str],
    input_file: Optional[click.Path],
):
    """Set state."""
    state_service = (
        state_service_from_job_id(project, job_id) or ctx.obj[STATE_SERVICE_KEY]
    )

    if input_file and state:
        raise ValueError("TODO: better error here")
    elif input_file:
        with open(input_file) as state_f:
            state_service.set_state(job_id, state_f.read())
    elif state:
        state_service.set_state(job_id, state)
    else:
        raise ValueError("TODO: better error here")


@meltano_state.command(name="get")
@click.argument("job_id")
@pass_project(migrate=True)
@click.pass_context
def get_state(ctx: click.Context, project: Project, job_id: str):  # noqa: WPS463
    """Get state."""
    state_service = (
        state_service_from_job_id(project, job_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    click.echo(json.dumps(state_service.get_state(job_id)))


@meltano_state.command(name="clear")
@click.argument("job_id")
@pass_project(migrate=True)
@click.pass_context
def clear_state(ctx: click.Context, project: Project, job_id: str):
    """Clear state."""
    state_service = (
        state_service_from_job_id(project, job_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    state_service.clear_state(job_id)
