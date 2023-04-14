"""Doc CLI command."""
from __future__ import annotations

import click

from meltano.cli.utils import InstrumentedCmd


@click.command(
    cls=InstrumentedCmd,
    short_help="Open the Meltano docs in your browser.",
)
def docs():
    """Open the Meltano docs in the system browser."""
    click.launch("https://docs.meltano.com/")
