import subprocess
import logging

from .venv_service import VenvService
from .plugin import PluginType


class DbtService:
    def __init__(self, project, venv_service: VenvService = None):
        self.project = project
        self.venv_service = venv_service or VenvService(project)
        self.transform_dir = f"{self.project.root}/transform/"
        self.profile_dir = f"{self.project.root}/transform/profile/"

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    def call(self, *args):
        logging.debug(f"Invoking: dbt {args}")
        exec_args = list(map(str, [self.exec_path, *args]))
        run = subprocess.run(exec_args, cwd=self.transform_dir)

        run.check_returncode()
        return run

    def compile(self, models=None):
        params = ["compile", "--profiles-dir", self.profile_dir, "--profile", "meltano"]
        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        return self.call(*params)

    def deps(self):
        return self.call("deps", "--profiles-dir", self.profile_dir)

    def run(self, models=None):
        params = ["run", "--profiles-dir", self.profile_dir, "--profile", "meltano"]
        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        return self.call(*params)
