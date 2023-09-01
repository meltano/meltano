"""Open the Meltano Cloud Documentation."""

from __future__ import annotations

import click


@click.command(
    short_help="Open the Meltano Cloud docs in your browser.",
)
def docs():
    """Open the Meltano Cloud docs in the system browser."""
    click.launch("https://docs.meltano.com/cloud")
    click.secho("Opening the docs...", fg="green")
