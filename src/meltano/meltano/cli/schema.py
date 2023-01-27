"""Schema creation CLI."""

from __future__ import annotations

import click

from meltano.core.db import ensure_schema_exists, project_engine

from . import cli
from .params import pass_project
from .utils import InstrumentedCmd, InstrumentedGroup


@cli.group(cls=InstrumentedGroup, short_help="Manage system DB schema.")
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
    ensure_schema_exists(engine, schema_name, grant_roles=roles)
