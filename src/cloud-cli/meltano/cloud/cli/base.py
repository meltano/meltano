"""Meltano Cloud CLI base command group."""

from __future__ import annotations

import click


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option()
def cloud() -> None:
    """Interface with Meltano Cloud."""
