import os
import click
from pathlib import Path
from sqlalchemy import create_engine
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command

from meltano.core.migration_service import MigrationService
from meltano.core.db import project_engine
from . import cli
from .params import project, db_options


@cli.command()
@db_options
@click.pass_context
def upgrade(ctx, engine_uri):
    engine = create_engine(engine_uri)

    migration_service = MigrationService(engine)
    migration_service.upgrade()
