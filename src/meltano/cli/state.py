"""State management in CLI."""

from __future__ import annotations

import json
import re
import typing as t
from datetime import datetime as dt
from datetime import timezone as tz
from functools import partial, reduce
from operator import xor
from pathlib import Path

import click
import structlog

from meltano.cli.params import pass_project
from meltano.cli.utils import CliEnvironmentBehavior, InstrumentedCmd, InstrumentedGroup
from meltano.core.block.parser import BlockParser
from meltano.core.db import project_engine
from meltano.core.job import Payload
from meltano.core.state_service import InvalidJobStateError, StateService

if t.TYPE_CHECKING:
    from meltano.core.project import Project

STATE_SERVICE_KEY = "state_service"

logger = structlog.getLogger(__name__)


class MutuallyExclusiveOptionsError(Exception):
    """Mutually exclusive options are provided incorrectly."""

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


def _prompt_for_confirmation(prompt):  # noqa: ANN001, ANN202
    """Wrap destructive CLI commands which should prompt the user for confirmation."""

    def _prompt_callback(ctx: click.Context, param, value: bool) -> None:  # noqa: ANN001, ARG001, FBT001
        if not value and not click.confirm(prompt):
            ctx.exit(1)

    return click.option(
        "--force",
        is_flag=True,
        expose_value=False,
        callback=_prompt_callback,
        help="Don't prompt for confirmation.",
    )


prompt_for_confirmation = partial(
    _prompt_for_confirmation,
    prompt="This is a destructive command. Continue?",
)


def state_service_from_state_id(project: Project, state_id: str) -> StateService | None:
    """Instantiate by parsing a state_id."""
    state_id_re = re.compile(
        r"^(?P<env>.+):(?P<tap>.+)-to-(?P<target>.+?)(?:\:(?P<suffix>.+))?(?<=[^\:])$",
    )
    if match := state_id_re.match(state_id):
        # If the state_id matches convention (i.e., job has been run via "meltano run"),
        # try parsing into BlockSet.
        # This way, we get BlockSet validation and raise an error if no
        # plugin in the BlockSet has "state" capability
        try:
            if not project.environment:
                logger.warning(
                    "Running state operation for environment "  # noqa: G004
                    f"'{match['env']}' outside of an environment",
                )

            elif project.environment.name != match["env"]:
                logger.warning(
                    f"Environment '{match['env']}' used in state operation does "  # noqa: G004
                    f"not match current environment '{project.environment.name}'.",
                )

            project.activate_environment(match["env"])
            blocks = [match["tap"], match["target"]]
            parser = BlockParser(logger, project, blocks)
            return next(parser.find_blocks()).state_service
        except Exception:
            logger.warning("No plugins found for provided state_id.")
    # If provided state_id does not match convention (i.e., run via "meltano elt"),
    # use the standalone StateService in the CLI context.
    return None


@click.group(
    cls=InstrumentedGroup,
    name="state",
    short_help="Manage Singer state.",
    environment_behavior=CliEnvironmentBehavior.environment_optional_ignore_default,
)
@click.pass_context
@pass_project(migrate=True)
def meltano_state(project: Project, ctx: click.Context) -> None:
    """Manage state.

    \b
    Read more at https://docs.meltano.com/reference/command-line-interface#state
    """  # noqa: D301
    _, sessionmaker = project_engine(project)
    session = sessionmaker(future=True)
    ctx.obj[STATE_SERVICE_KEY] = StateService(project, session)


@meltano_state.command(cls=InstrumentedCmd, name="list")
@click.option("--pattern", type=str, help="Filter state IDs by pattern.")
@click.pass_context
def list_state(ctx: click.Context, pattern: str | None) -> None:
    """List all state_ids for this project.

    Optionally pass a glob-style pattern to filter state_ids by.
    """
    state_service: StateService = ctx.obj[STATE_SERVICE_KEY]
    if states := state_service.list_state(pattern):
        for state_id, state in states.items():
            if state:
                try:
                    state_service.validate_state(state)
                except (InvalidJobStateError, json.decoder.JSONDecodeError):
                    click.secho(state_id, fg="red")
                else:
                    click.secho(state_id, fg="green")
            else:
                click.secho(state_id, fg="yellow")
    else:
        logger.info("No state IDs found.")


@meltano_state.command(cls=InstrumentedCmd, name="copy")
@prompt_for_confirmation(
    prompt="This will overwrite state for the destination. Continue?",
)
@click.argument("src-state-id", type=str)
@click.argument("dst-state-id", type=str)
@pass_project(migrate=True)
@click.pass_context
def copy_state(
    ctx: click.Context,
    project: Project,
    src_state_id: str,
    dst_state_id: str,
) -> None:
    """Copy state to another job ID."""
    # Retrieve state for copying
    state_service: StateService = (
        state_service_from_state_id(project, src_state_id) or ctx.obj[STATE_SERVICE_KEY]
    )

    state_service.copy_state(src_state_id, dst_state_id)

    logger.info(
        f"State for {dst_state_id} was successfully copied from "  # noqa: G004
        f"{src_state_id} at {dt.now(tz=tz.utc):%Y-%m-%d %H:%M:%S%z}.",
    )


@meltano_state.command(cls=InstrumentedCmd, name="move")
@prompt_for_confirmation(
    prompt=(
        "This will clear the source state and overwrite destination state. Continue?"
    ),
)
@click.argument("src-state-id", type=str)
@click.argument("dst-state-id", type=str)
@pass_project(migrate=True)
@click.pass_context
def move_state(
    ctx: click.Context,
    project: Project,
    src_state_id: str,
    dst_state_id: str,
) -> None:
    """Move state to another job ID, clearing the original."""
    # Retrieve state for moveing
    state_service: StateService = (
        state_service_from_state_id(project, dst_state_id) or ctx.obj[STATE_SERVICE_KEY]
    )

    state_service.move_state(src_state_id, dst_state_id)

    logger.info(
        f"State for {src_state_id} was successfully moved to {dst_state_id} "  # noqa: G004
        f"at {dt.now(tz=tz.utc):%Y-%m-%d %H:%M:%S%z}.",
    )


@meltano_state.command(cls=InstrumentedCmd, name="merge")
@click.option(
    "--from-state-id",
    type=str,
    help="Merge state from an existing state ID.",
)
@click.option(
    "--input-file",
    type=click.Path(exists=True, path_type=Path),
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
    state: str | None,
    input_file: Path | None,
    from_state_id: str | None,
) -> None:
    """Add bookmarks to existing state."""
    state_service: StateService = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    mutually_exclusive_options = {
        "--input-file": input_file,
        "STATE": state,
        "--from-state-id": from_state_id,
    }
    if not reduce(xor, (bool(x) for x in mutually_exclusive_options.values())):
        raise MutuallyExclusiveOptionsError(*mutually_exclusive_options)
    if input_file:
        with input_file.open() as state_f:
            state_service.add_state(
                state_id,
                state_f.read(),
                payload_flags=Payload.INCOMPLETE_STATE,
            )
    elif state:
        state_service.add_state(state_id, state, payload_flags=Payload.INCOMPLETE_STATE)
    elif from_state_id:
        state_service.merge_state(from_state_id, state_id)
    logger.info(
        f"State for {state_id} was successfully "  # noqa: G004
        f"merged at {dt.now(tz=tz.utc):%Y-%m-%d %H:%M:%S%z}.",
    )


@meltano_state.command(cls=InstrumentedCmd, name="set")
@prompt_for_confirmation(
    prompt="This will overwrite the state's current value. Continue?",
)
@click.option(
    "--input-file",
    type=click.Path(exists=True, path_type=Path),
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
    state: str | None,
    input_file: Path | None,
) -> None:
    """Set state."""
    state_service: StateService = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    mutually_exclusive_options = {
        "--input-file": input_file,
        "STATE": state,
    }
    if not reduce(xor, (bool(x) for x in mutually_exclusive_options.values())):
        raise MutuallyExclusiveOptionsError(*mutually_exclusive_options)
    if input_file:
        with input_file.open() as state_f:
            state_service.set_state(state_id, state_f.read())
    elif state:
        state_service.set_state(state_id, state)
    logger.info(
        f"State for {state_id} was successfully set "  # noqa: G004
        f"at {dt.now(tz=tz.utc):%Y-%m-%d %H:%M:%S%z}.",
    )


@meltano_state.command(cls=InstrumentedCmd, name="get")
@click.argument("state-id")
@pass_project(migrate=True)
@click.pass_context
def get_state(ctx: click.Context, project: Project, state_id: str) -> None:
    """Get state."""
    state_service: StateService = (
        state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
    )
    retrieved_state = state_service.get_state(state_id)
    click.echo(json.dumps(retrieved_state))


@meltano_state.command(cls=InstrumentedCmd, name="clear")
@prompt_for_confirmation(prompt="This will clear state for the job(s). Continue?")
@click.argument("state-id", required=False)
@click.option(
    "--all",
    "clear_all",
    is_flag=True,
    required=False,
    help="Clear all states IDs.",
)
@pass_project(migrate=True)
@click.pass_context
def clear_state(
    ctx: click.Context,
    project: Project,
    state_id: str | None,
    clear_all: bool,  # noqa: FBT001
) -> None:
    """Clear state."""
    # Case where neither or both have been provided
    if bool(state_id) == clear_all:
        msg = "A state ID or the --all flag must be provided, but not both"
        raise click.UsageError(msg)
    if state_id:
        state_service: StateService = (
            state_service_from_state_id(project, state_id) or ctx.obj[STATE_SERVICE_KEY]
        )
        state_service.clear_state(state_id)
    if clear_all:
        state_service: StateService = ctx.obj[STATE_SERVICE_KEY]
        count = state_service.clear_all_states()
        msg = f"{count} state(s) were successfully cleared"
        logger.info(msg)
