import os
import logging
import psutil
import importlib
import meltano
import subprocess
import signal
import shutil
from typing import Optional

from meltano.core.project import Project
from meltano.core.migration_service import MigrationService
import meltano.core.compiler.project_compiler
import meltano.core.bundle as bundle


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

    def upgrade_package(self, pip_url: Optional[str] = None, force=False):
        # we need to find out if the `meltano` module is installed as editable
        editable = meltano.__file__.endswith("src/meltano/__init__.py")
        editable = editable and not force

        if editable:
            logging.info(
                f"Skipping `meltano` upgrade because Meltano is installed as editable."
            )
        else:
            pip_url = pip_url or "meltano"
            run = subprocess.run(
                ["pip", "install", "--upgrade", pip_url],
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if run.returncode != 0:
                raise UpgradeError(f"Failed to upgrade `meltano`.", run)

    def upgrade_files(self):
        """
        Update the files managed by Meltano inside the current project.
        """
        files_map = {
            bundle.find("dags/meltano.py"): self.project.root_dir(
                "orchestrate/dags/meltano.py"
            ),
            bundle.find("transform/profile/profiles.yml"): self.project.root_dir(
                "transform/profile/profiles.yml"
            ),
            bundle.find(".gitignore"): self.project.root_dir(".gitignore"),
        }

        for src, dst in files_map.items():
            try:
                shutil.copy(src, dst)
                logging.info(f"{dst} has been updated.")
            except Exception as err:
                logging.error(f"Meltano could not update {dst}: {err}")

    def compile_models(self):
        # Make sure we load the _new_ Meltano version's ProjectCompiler
        importlib.reload(meltano.core.compiler.project_compiler)
        from meltano.core.compiler.project_compiler import ProjectCompiler

        ProjectCompiler(self.project).compile()

    def upgrade(self, **kwargs):
        self.upgrade_package(**kwargs)
        self.upgrade_files()

        self.migration_service.upgrade()
        self.migration_service.seed(self.project)

        self.compile_models()
