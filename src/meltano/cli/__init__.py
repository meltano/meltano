"""Main entry point for the meltano CLI."""
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
    model,
    remove,
    repl,
    schedule,
    schema,
    select,
    ui,
    upgrade,
    user,
    run,
    validate,
)

setup_logging()

logger = logging.getLogger(__name__)


def main():
    """Entry point for the meltano cli."""
    # mark the current process as executed via the `cli`
    os.environ["MELTANO_JOB_TRIGGER"] = os.getenv("MELTANO_JOB_TRIGGER", "cli")
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
