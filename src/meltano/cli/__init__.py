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
    select,
    version,
)


def main():
    cli(obj={"project": None})
