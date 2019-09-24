import os
import logging
import psutil
import meltano
import subprocess
import signal

from meltano.core.project import Project
from meltano.core.migration_service import MigrationService


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


class UpgradeService:
    def __init__(
        self, engine, project: Project, migration_service: MigrationService = None
    ):
        self.project = project
        self.migration_service = migration_service or MigrationService(engine)

    def reload(self):
        pid_file_path = self.project.run_dir("gunicorn.pid")
        try:
            with pid_file_path.open("r") as pid_file:
                pid = int(pid_file.read())

                process = psutil.Process(pid)
                process.send_signal(signal.SIGHUP)
        except Exception as ex:
            logging.error(f"Cannot restart from `{pid_file_path}`: {ex}")

    def upgrade(self):
        # we need to find out if the `meltano` module is installed as editable
        editable = meltano.__file__.endswith("src/meltano/__init__.py")

        if editable:
            logging.info(
                f"Skipping `meltano` upgrade because Meltano is installed as editable."
            )
        else:
            run = subprocess.run(
                ["pip", "install", "-U", "meltano"],
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if run.returncode != 0:
                raise UpgradeError(f"Failed to upgrade `meltano`.", run)

        self.migration_service.upgrade()
