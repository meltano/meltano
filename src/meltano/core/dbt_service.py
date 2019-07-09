import subprocess
import logging

from .config_service import ConfigService
from .db import project_engine
from .plugin import PluginType
from .plugin_invoker import invoker_factory
from .venv_service import VenvService


class DbtService:
    def __init__(self, project):
        self.project = project
        self._plugin = ConfigService(project).find_plugin(
            "dbt", PluginType.TRANSFORMERS
        )
        self.profile_dir = f"{self.project.root}/transform/profile/"
        _, self._Session = project_engine(project)

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    def compile(self, models=None, **kwargs):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)

        try:
            params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
            if models:
                # Always include the my_meltano_project model
                all_models = f"{models} my_meltano_project"
                params.extend(["--models", all_models])

            handle = invoker.invoke("compile", *params, **kwargs)
            handle.wait()

            return handle
        finally:
            session.close()

    def deps(self):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)
        try:
            handle = invoker.invoke("deps")
            handle.wait()

            return handle
        finally:
            session.close()

    def run(self, models=None, **kwargs):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)

        try:
            params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
            if models:
                # Always include the my_meltano_project model
                all_models = f"{models} my_meltano_project"
                params.extend(["--models", all_models])

            handle = invoker.invoke("run", *params, **kwargs)
            handle.wait()

            return handle
        finally:
            session.close()
