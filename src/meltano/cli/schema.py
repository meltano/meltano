"""Schema creation CLI."""

from __future__ import annotations

import click

from meltano.cli.params import pass_project
from meltano.cli.utils import InstrumentedCmd, InstrumentedGroup
from meltano.core.db import ensure_schema_exists, project_engine


@click.group(cls=InstrumentedGroup, short_help="Manage system DB schema.")
def schema() -> None:
    """Manage system DB schema."""


@schema.command(
    cls=InstrumentedCmd,
    short_help="Create system DB schema, if not exists.",
)
@click.argument("schema")
@click.argument("roles", nargs=-1, required=True)
@pass_project()
def create(project, schema_name, roles) -> None:  # noqa: ANN001
    """Create system DB schema, if not exists."""
    engine, _ = project_engine(project)
    ensure_schema_exists(engine, schema_name, grant_roles=roles)
