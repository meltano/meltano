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
from . import cli
from .params import project, db_options


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


def restart_process(pid):
    process = psutil.Process(pid)

    command = process.cmdline()
    process.terminate()
    process.wait()

    subprocess.Popen(command)


@cli.command()
@project
@click.pass_context
def upgrade(ctx, project):
    # we need to find out if the `meltano` module is installed as editable
    editable = meltano.__file__.endswith("src/meltano/__init__.py")

    if editable:
        logging.info(
            f"Skipping `meltano` upgrade because Meltano is installed as editable."
        )
    else:
        run = subprocess.run(
            ["pip", "install", "-U", "meltano"],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise UpgradeError(f"Failed to install plugin '{name}'.", run)

    # run the db migration
    engine, _ = project_engine(project)
    migration_service = MigrationService(engine)
    migration_service.upgrade()

    def try_restart(pid_file_path):
        try:
            with pid_file_path.open("r") as pid_file:
                pid = int(pid_file.read())
                restart_process(pid)
        except:
            logging.debug(f"Cannot restart from `{pid_file_path}`.")

    try_restart(project.run_dir("flask.pid"))
    try_restart(project.run_dir("gunicorn.pid"))
