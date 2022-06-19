"""Main entry point for the meltano CLI."""
from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

from meltano.core.logging import setup_logging
from meltano.core.project import ProjectReadonly

from . import commands  # noqa: F401
from .cli import cli
from .utils import CliError

if TYPE_CHECKING:
    from meltano.core.tracking.tracker import Tracker


# Holds the exit code for error reporting during process exiting. In particular, a function
# registered by the `atexit` module uses this value.
exit_code: None | int = None

atexit_handler_registered = False
exit_code_reported = False
exit_event_tracker: Tracker = None

setup_logging()

logger = logging.getLogger(__name__)


def _run_cli():
    """Run the Meltano CLI."""
    try:
        try:  # noqa: WPS505
            cli(obj={"project": None})
        except ProjectReadonly as err:
            raise CliError(
                f"The requested action could not be completed: {err}"
            ) from err
        except Exception as err:
            raise CliError(str(err)) from err
    except CliError as cli_error:
        cli_error.print()
        sys.exit(1)


def main():
    """Entry point for the meltano CLI."""
    # Mark the current process as executed via the CLI
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
