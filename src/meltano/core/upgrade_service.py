import os
import logging
import psutil
import meltano
import subprocess

from meltano.core.project import Project


class UpgradeError(Exception):
    """Occurs when the Meltano upgrade fails"""

    pass


class UpgradeService:
    def __init__(self, project: Project):
        self.project = project

    def restart_server(self):
        def try_restart(pid_file_path):
            try:
                with pid_file_path.open("r") as pid_file:
                    pid = int(pid_file.read())
                    self.restart_process(pid)
            except Exception as ex:
                logging.debug(f"Cannot restart from `{pid_file_path}`: {ex}")

        try_restart(self.project.run_dir("flask.pid"))
        try_restart(self.project.run_dir("gunicorn.pid"))

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
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if run.returncode != 0:
                raise UpgradeError(f"Failed to upgrade `meltano`.", run)

    def restart_process(self, pid):
        process = psutil.Process(pid)
        logging.info(f"Restarting process {process.name}({pid})...")

        command = process.cmdline()
        process.terminate()
        process.wait()

        subprocess.Popen(command)
