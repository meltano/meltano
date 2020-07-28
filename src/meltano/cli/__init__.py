import os
import sys
import click
import logging

from meltano.core.logging import setup_logging
from meltano.core.project import ProjectReadonly
from .cli import cli
from .utils import CliError
from . import (
    elt,
    schema,
    discovery,
    initialize,
    add,
    install,
    invoke,
    ui,
    upgrade,
    schedule,
    select,
    repl,
    config,
    model,
    user,
)

setup_logging()

logger = logging.getLogger(__name__)


def main():
    # mark the current process as executed via the `cli`
    os.environ["MELTANO_JOB_TRIGGER"] = os.getenv("MELTANO_JOB_TRIGGER", "cli")
    try:
        try:
            cli(obj={"project": None})
        except ProjectReadonly as err:
            raise CliError(
                f"The requested action could not be completed: {err}"
            ) from err
    except CliError as err:
        logger.debug(str(err), exc_info=True)
        click.secho(str(err), fg="red")
        sys.exit(1)
