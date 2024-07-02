"""Fun Dragon CLI command."""

from __future__ import annotations

import random

import click

from meltano.core.cli_messages import (
    DRAGON_0,
    DRAGON_1,
    DRAGON_2,
    DRAGON_3,
    DRAGON_4,
    MELTY,
)


@click.command(short_help="Summon a dragon!")
def dragon() -> None:
    """Summon a dragon."""
    dragon_list = [
        MELTY,
        DRAGON_0,
        DRAGON_1,
        DRAGON_2,
        DRAGON_3,
        DRAGON_4,
    ]
    click.secho(random.choice(dragon_list), nl=False)  # noqa: S311
