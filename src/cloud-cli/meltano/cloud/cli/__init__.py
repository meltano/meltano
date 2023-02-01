"""Meltano Cloud CLI."""

from __future__ import annotations

import click


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
def cloud() -> None:
    """Run the Meltano Cloud CLI as a Click command."""
    click.echo("Meltano Cloud CLI placeholder output")


def main() -> int:
    """Run the Meltano Cloud CLI.

    Returns:
        The CLI exit code.
    """
    try:
        cloud()
    except Exception:
        return 1
    return 0
