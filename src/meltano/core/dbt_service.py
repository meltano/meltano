import subprocess
import logging


class DbtService:
    def __init__(self, project):
        self.project = project

    @property
    def exec_path(self):
        return self.project.venvs_dir("dbt", "bin", "dbt")

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
        return self.call("deps")

    def run(self):
        return self.call(
            "run", "--profiles-dir", self.project.root, "--profile", "meltano"
        )
