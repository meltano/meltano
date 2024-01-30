"""Main entry point for the meltano CLI."""

from __future__ import annotations

import os
import sys
import typing as t

import structlog

from meltano.cli import (  # noqa: WPS235
    add,
    config,
    docs,
    dragon,
    elt,
    environment,
    hub,
    initialize,
    install,
    invoke,
    job,
    lock,
    remove,
    run,
    schedule,
    schema,
    select,
    state,
    upgrade,
    validate,
)
from meltano.cli import compile as compile_module
from meltano.cli.cli import cli
from meltano.cli.utils import CliError
from meltano.core.error import MeltanoError, ProjectReadonly
from meltano.core.logging import setup_logging

if t.TYPE_CHECKING:
    from meltano.core.tracking.tracker import Tracker

cli.add_command(add.add)
cli.add_command(compile_module.compile_command)
cli.add_command(config.config)
cli.add_command(docs.docs)
cli.add_command(dragon.dragon)
cli.add_command(elt.el)
cli.add_command(elt.elt)
cli.add_command(environment.meltano_environment)
cli.add_command(hub.hub)
cli.add_command(initialize.init)
cli.add_command(install.install)
cli.add_command(invoke.invoke)
cli.add_command(lock.lock)
cli.add_command(remove.remove)
cli.add_command(schedule.schedule)
cli.add_command(schema.schema)
cli.add_command(select.select)
cli.add_command(state.meltano_state)
cli.add_command(upgrade.upgrade)
cli.add_command(run.run)
cli.add_command(validate.test)
cli.add_command(job.job)

# Holds the exit code for error reporting during process exiting. In
# particular, a function registered by the `atexit` module uses this value.
exit_code: None | int = None

atexit_handler_registered = False
exit_code_reported = False
exit_event_tracker: Tracker | None = None

setup_logging()

logger = structlog.stdlib.get_logger(__name__)

troubleshooting_message = """\
Need help fixing this problem? Visit http://melta.no/ for troubleshooting steps, or to
join our friendly Slack community.
"""


def handle_meltano_error(error: MeltanoError) -> t.NoReturn:
    """Handle a MeltanoError.

    Args:
        error: The error to handle.

    Raises:
        CliError: always.
    """
    raise CliError(str(error)) from error


def _run_cli():
    """Run the Meltano CLI.

    Raises:
        KeyboardInterrupt: if caught.
    """
    try:
        try:  # noqa: WPS225, WPS505
            cli(obj={"project": None})
        except ProjectReadonly as err:
            raise CliError(
                f"The requested action could not be completed: {err}",  # noqa: EM102
            ) from err
        except KeyboardInterrupt:  # noqa: WPS329
            raise
        except MeltanoError as err:
            handle_meltano_error(err)
        except Exception as err:
            raise CliError(f"{troubleshooting_message}\n{err}") from err  # noqa: EM102
    except CliError as cli_error:
        cli_error.print()
        sys.exit(1)


def main():
    """Entry point for the meltano CLI."""
    # Mark the current process as executed via the CLI
    logging.captureWarnings(capture=True)
    os.environ["MELTANO_JOB_TRIGGER"] = os.getenv("MELTANO_JOB_TRIGGER", "cli")
    try:
        _run_cli()
    finally:
        global exit_code
        ex = sys.exc_info()[1]
        if ex is None:
            exit_code = 0  # noqa: WPS442
        elif isinstance(ex, SystemExit):
            exit_code = 0 if ex.code is None else ex.code  # noqa: WPS442
        else:
            exit_code = 1  # noqa: WPS442
        # Track the exit event now to provide more details via the exception context.
        # We assume the process will exit practically immediately after `main` returns.
        if exit_event_tracker is not None:
            exit_event_tracker.track_exit_event()
