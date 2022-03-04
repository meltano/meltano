"""Fun Dragon CLI command"""
import click
import random

from meltano.core.cli_messages import (
    MELTY,
    DRAGON_0, 
    DRAGON_1, 
    DRAGON_2,
    DRAGON_3,
    DRAGON_4
)

from . import cli


@cli.command(short_help="Spawn a dragon!")
@click.pass_context
def dragon(ctx):
    """
    Does what it says!
    """
    dragon_list = [
        MELTY,
        DRAGON_0,
        DRAGON_1,
        DRAGON_2,
        DRAGON_3,
        DRAGON_4,
    ]
    click.secho(random.choice(dragon_list), nl=False)
