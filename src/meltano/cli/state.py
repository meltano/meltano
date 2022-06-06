"""State management in CLI."""
import json
import re
from datetime import datetime as dt
from functools import partial, reduce, wraps
from operator import xor
from typing import Optional

import click
import structlog

from meltano.cli.params import pass_project
from meltano.core.block.parser import BlockParser
from meltano.core.db import project_engine
from meltano.core.job import Payload
from meltano.core.legacy_tracking import LegacyTracker
from meltano.core.project import Project
from meltano.core.state_service import InvalidJobStateError, StateService

from . import cli

STATE_SERVICE_KEY = "state_service"

logger = structlog.getLogger(__name__)


class MutuallyExclusiveOptionsError(Exception):
    """Occurs when mutually exclusive options are provided incorrectly."""

    def __init__(self, *options: str) -> None:
        """Instantiate the error.

        Args:
            options: the mutually exclusive options that were incorrectly provided.
        """
        super().__init__(*options)
        self.options = options

    def __str__(self) -> str:
        """Represent the error as a string."""
        return f"Must provide exactly one of: {','.join(self.options)}"


def _prompt_for_confirmation(prompt):
    """Wrap destructive CLI commands which should prompt the user for confirmation."""

    def wrapper(func):
        fun = click.option(
            "--force", is_flag=True, help="Don't prompt for confirmation."
        )(func)

        @wraps(func)
        def _wrapper(force=False, *args, **kwargs):
            if force or click.confirm(prompt):
                return fun(*args, **kwargs, force=force)
            else:
                click.secho("Aborting.", fg="red")

        return _wrapper

    return wrapper


prompt_for_confirmation = partial(
    _prompt_for_confirmation, prompt="This is a destructive command. Continue?"
)


def state_service_from_state_id(
    project: Project, state_id: str
) -> Optional[StateService]:
    """Instantiate by parsing a state_id."""
    state_id_re = re.compile(r"^(?P<env>.+)\:(?P<tap>.+)-to-(?P<target>.+)$")
    match = state_id_re.match(state_id)
    if match:
        # If the state_id matches convention (i.e., job has been run via "meltano run"),
        # try parsing into BlockSet.
        # This way, we get BlockSet validation and raise an error if no
        # plugin in the BlockSet has "state" capability
        try:
            if not project.active_environment:
                logger.warn(
                    f"Running state operation for environment '{match.group('env')}' outside of an environment"
                )
            elif project.active_environment.name != match.group("env"):
                logger.warn(
                    f"Environment '{match.group('env')}' used in state operation does not match current environment '{project.active_environment.name}'."
                )
            project.activate_environment(match.group("env"))
            blocks = [match.group("tap"), match.group("target")]
            parser = BlockParser(logger, project, blocks)
            return next(parser.find_blocks()).state_service
        except Exception:
            logger.warn("No plugins found for provided state_id.")
    # If provided state_id does not match convention (i.e., run via "meltano elt"),
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
@click.argument("pattern", required=False)
@click.pass_context
@pass_project()
def list_state(
    project: Project, ctx: click.Context, pattern: Optional[str]
):  # noqa: WPS125
    """List all state_ids for this project.

    Optionally pass a glob-style pattern to filter state_ids by.
    """
    state_service = ctx.obj[STATE_SERVICE_KEY]
    tracker = LegacyTracker(project)
    tracker.track_meltano_state("list")
    states = state_service.list_state(pattern)
    if states:
        for state_id, state in states.items():
            if state:
                try:
                    state_service.validate_state(json.dumps(state))
                except (InvalidJobStateError, json.decoder.JSONDecodeError):
                    click.secho(state_id, fg="red")
                else:
                    click.secho(state_id, fg="green")
            else:
                click.secho(state_id, fg="yellow")
    else:
        logger.info("No state IDs found.")


@meltano_state.command(name="merge")
@click.option(
    "--from-state-id",
    type=str,
    help="Merge state from an existing state ID.",
)
@click.option(
    "--input-file",
    type=click.Path(exists=True),
    help="Merge state from a JSON file containing Singer state.",
)
@click.argument("state-id", type=str)
@click.argument("state", type=str, required=False)
@pass_project(migrate=True)
@click.pass_context
def merge_state(
    ctx: click.Context,
    project: Project,
    state_id: str,
    state: Optional[str],
    input_file: Optional[click.Path],
    from_state_id: Optional[str],
):
    """Add bookmarks to existing state."""
    state_service = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    tracker = LegacyTracker(project)
    tracker.track_meltano_state("merge", state_id)
    mutually_exclusive_options = ["--input-file", "STATE", "--from-state-id"]
    if not reduce(xor, map(bool, [state, input_file, from_state_id])):
        raise MutuallyExclusiveOptionsError(*mutually_exclusive_options)
    elif input_file:
        with open(input_file) as state_f:
            state_service.add_state(
                state_id, state_f.read(), payload_flags=Payload.INCOMPLETE_STATE
            )
    elif state:
        state_service.add_state(state_id, state, payload_flags=Payload.INCOMPLETE_STATE)
    elif from_state_id:
        state_service.merge_state(from_state_id, state_id)
    logger.info(
        f"State for {state_id} was successfully merged at {dt.utcnow():%Y-%m-%d %H:%M:%S}."  # noqa: WPS323
    )


@meltano_state.command(name="set")
@prompt_for_confirmation(
    prompt="This will overwrite the state's current value. Continue?"
)
@click.option(
    "--input-file",
    type=click.Path(exists=True),
    help="Set state from json file containing Singer state.",
)
@click.argument("state-id")
@click.argument("state", type=str, required=False)
@pass_project(migrate=True)
@click.pass_context
def set_state(
    ctx: click.Context,
    project: Project,
    state_id: str,
    state: Optional[str],
    input_file: Optional[click.Path],
    force: bool,
):
    """Set state."""
    state_service = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    tracker = LegacyTracker(project)
    tracker.track_meltano_state("set", state_id)
    if not reduce(xor, map(bool, [state, input_file])):
        raise MutuallyExclusiveOptionsError("--input-file", "STATE")
    elif input_file:
        with open(input_file) as state_f:
            state_service.set_state(state_id, state_f.read())
    elif state:
        state_service.set_state(state_id, state)
    logger.info(
        f"State for {state_id} was successfully set at {dt.utcnow():%Y-%m-%d %H:%M:%S}."  # noqa: WPS323
    )


@meltano_state.command(name="get")  # noqa: WPS46
@click.argument("state-id")
@pass_project(migrate=True)
@click.pass_context
def get_state(ctx: click.Context, project: Project, state_id: str):  # noqa: WPS463
    """Get state."""
    state_service = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    tracker = LegacyTracker(project)
    tracker.track_meltano_state("get", state_id)
    retrieved_state = state_service.get_state(state_id)
    click.echo(json.dumps(retrieved_state))


@meltano_state.command(name="clear")
@prompt_for_confirmation(prompt="This will clear state for the job. Continue?")
@click.argument("state-id")
@pass_project(migrate=True)
@click.pass_context
def clear_state(ctx: click.Context, project: Project, state_id: str, force: bool):
    """Clear state."""
    state_service = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    tracker = LegacyTracker(project)
    tracker.track_meltano_state("clear", state_id)
    state_service.clear_state(state_id)
