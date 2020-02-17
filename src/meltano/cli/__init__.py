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
    permissions,
    schedule,
    select,
    repl,
    config,
    model,
    user,
)


def main():
    cli(obj={"project": None})
