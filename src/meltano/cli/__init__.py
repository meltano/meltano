"""Main entry point for the meltano CLI."""
from __future__ import annotations

import logging
import os
import sys

from meltano.core.logging import setup_logging
from meltano.core.project import ProjectReadonly

from .utils import CliError

# TODO: Importing the cli.cli module breaks other cli module imports
# This suggests a cyclic dependency or a poorly structured interface.
# This should be investigated and resolved to avoid implicit behavior
# based solely on import order.
from .cli import cli  # isort:skip
from . import (  # isort:skip # noqa: F401, WPS235
    add,
    config,
    discovery,
    dragon,
    elt,
    environment,
    initialize,
    install,
    invoke,
    remove,
    repl,
    schedule,
    schema,
    select,
    state,
    ui,
    upgrade,
    user,
    run,
    validate,
    job,
)

# Holds the exit code for error reporting during process exiting. In particular, a function
# registered by the `atexit` module uses this value.
exit_code: None | int = None

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
        except KeyboardInterrupt:  # noqa: WPS329
            raise
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
            exit_code = 0
        elif isinstance(ex, SystemExit):
            exit_code = 0 if ex.code is None else ex.code
        else:
            exit_code = 1
