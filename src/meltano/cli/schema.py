"""Schema creation CLI."""

import click

from meltano.cli.cli import cli
from meltano.cli.params import pass_project
from meltano.cli.utils import InstrumentedCmd
from meltano.core.db import DB, project_engine


@cli.commands.schema  # Refer to `src/meltano/cli/commands.py`
def schema():
    """Manage system DB schema."""


@schema.command(
    cls=InstrumentedCmd, short_help="Create system DB schema, if not exists."
)
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
@pass_project()
def create(project, schema_name, roles):
    """Create system DB schema, if not exists."""
    engine, _ = project_engine(project)
    DB.ensure_schema_exists(engine, schema_name, grant_roles=roles)
