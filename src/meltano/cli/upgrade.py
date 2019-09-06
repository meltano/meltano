import os
import click
import subprocess
import psutil
import meltano
import logging
from pathlib import Path
from sqlalchemy import create_engine

from meltano.core.project import Project
from meltano.core.db import project_engine
from meltano.core.migration_service import MigrationService
from meltano.core.upgrade_service import UpgradeService
from . import cli
from .params import project, db_options


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


@cli.command()
@click.option(
    "--restart/--no-restart",
    help="Restart the running Meltano instance automatically.",
    default=False,
)
@project
@click.pass_context
def upgrade(ctx, project, restart):
    engine, _ = project_engine(project)
    upgrade_service = UpgradeService(engine, project)

    try:
        upgrade_service.upgrade()

        if restart:
            upgrade_service.restart_server()
    except UpgradeError as up:
        click.secho(str(up), fg="red")
        raise click.Abort()
