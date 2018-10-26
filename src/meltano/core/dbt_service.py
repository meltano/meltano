import subprocess
import logging

from .venv_service import VenvService


class DbtService:
    def __init__(self, project, venv_service: VenvService = None):
        self.project = project
        self.venv_service = venv_service or VenvService(project)

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt")

    def call(self, *args):
        logging.debug(f"Invoking: dbt {args}")
        exec_args = list(map(str, [self.exec_path, *args]))
        run = subprocess.run(exec_args)

        run.check_returncode()
        return run

    def compile(self):
        return self.call(
            "compile", "--profiles-dir", self.project.root, "--profile", "meltano"
        )

    def deps(self):
        return self.call("deps", "--profiles-dir", self.project.root)

    def run(self):
        return self.call(
            "run", "--profiles-dir", self.project.root, "--profile", "meltano"
        )
