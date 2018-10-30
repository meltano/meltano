import os
import yaml
import json
import subprocess

from .config_service import ConfigService
from .venv_service import VenvService
from .utils import noop
from .plugin import Plugin
from .project import Project


class PluginInstallError(Exception):
    """
    Happens when a plugin fails to install.
    """

    pass


class PluginInstallService:
    def __init__(
        self,
        project: Project,
        venv_service: VenvService = None,
        config_service: ConfigService = None,
    ):
        self.project = project
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or ConfigService(project)

    def create_venv(self, plugin: Plugin):
        return self.venv_service.create(namespace=plugin.type, name=plugin.name)

    def install_all_plugins(self, status_cb=noop):
        errors = []
        installed = []

        for plugin in self.config_service.plugins():
            status = {"plugin": plugin, "status": "running"}
            status_cb(status)

            try:
                self.create_venv(plugin)
                self.install_plugin(plugin)

                status["status"] = "success"
                installed.append(status)
                status_cb(status)
            except PluginInstallError as err:
                status["status"] = "error"
                status["message"] = str(err)
                errors.append(status)
                status_cb(status)

        return {"errors": errors, "installed": installed}

    def install_plugin(self, plugin: Plugin):
        try:
            install_result = self.venv_service.install(
                namespace=plugin.type, name=plugin.name, pip_url=plugin.pip_url
            )

            self.install_config_stub(plugin)
            return install_result
        except Exception as err:
            raise PluginInstallError()

    def install_config_stub(self, plugin: Plugin):
        plugin_dir = self.project.plugin_dir(plugin)
        os.makedirs(plugin_dir, exist_ok=True)

        # TODO: refactor as explicit stubs
        with open(plugin_dir.joinpath(plugin.config_files["config"]), "w") as config:
            json.dump(plugin.config, config)
