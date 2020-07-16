import os
import click

from meltano.core.project import ProjectReadonly
from .cli import cli
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


def main():
    # mark the current process as executed via the `cli`
    os.environ["MELTANO_JOB_TRIGGER"] = os.getenv("MELTANO_JOB_TRIGGER", "cli")

    try:
        cli(obj={"project": None})
    except ProjectReadonly as err:
        click.secho(f"The requested action could not be completed: {err}", fg="red")
