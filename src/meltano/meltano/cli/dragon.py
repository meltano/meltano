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

from . import cli


@cli.command(short_help="Summon a dragon!")
@click.pass_context
def dragon(ctx):
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
