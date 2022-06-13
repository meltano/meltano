import click

from meltano.core.db import DB, project_engine

from . import cli
from .params import pass_project


@cli.group(short_help="Manage system DB schema.")
def schema():
    """Manage system DB schema."""


@schema.command(short_help="Create system DB schema, if not exists.")
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
@pass_project()
def create(project, schema, roles):
    """Create system DB schema, if not exists."""
    engine, _ = project_engine(project)
    DB.ensure_schema_exists(engine, schema, grant_roles=roles)
