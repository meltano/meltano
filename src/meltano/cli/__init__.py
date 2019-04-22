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
    permissions,
    schedule,
    select,
)


def main():
    cli(obj={"project": None})
