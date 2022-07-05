"""Fun Dragon CLI command."""
import random

import click

from meltano.cli.cli import cli
from meltano.core.cli_messages import (
    DRAGON_0,
    DRAGON_1,
    DRAGON_2,
    DRAGON_3,
    DRAGON_4,
    MELTY,
)


@cli.commands.dragon  # Refer to `src/meltano/cli/commands.py`
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
