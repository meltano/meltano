import subprocess
import logging

from .venv_service import VenvService
from .plugin import PluginType
from .config_service import ConfigService
from .plugin_invoker import invoker_factory


class DbtService:
    def __init__(self, project):
        self.project = project
        self._plugin = ConfigService(project).get_plugin("dbt", PluginType.TRANSFORMERS)
        self.invoker = invoker_factory(project, self._plugin)
        self.profile_dir = f"{self.project.root}/transform/profile/"

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    def compile(self, models=None):
        params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        handle = self.invoker.invoke("compile", *params)
        handle.wait()

        return handle

    def deps(self):
        handle = self.invoker.invoke("deps")
        handle.wait()

        return handle

    def run(self, models=None):
        params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        handle = self.invoker.invoke("run", *params)
        handle.wait()

        return handle
