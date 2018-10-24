import os
import yaml
import subprocess

from meltano.support.project_add_service import ProjectAddService
from meltano.support.plugin_discovery_service import PluginDiscoveryService
from meltano.support.venv_service import VenvService
from .project import Project


class PluginInstallServicePluginNotFoundError(Exception):
    pass


class PluginInstallService:
    def __init__(self, project: Project, plugin_type, plugin_name,
                 discovery_service=None,
                 venv_service=None,
                 add_service=None):
        self.project = project
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        self.discovery_service = discovery_service or PluginDiscoveryService()
        self.venv_service = venv_service or VenvService(project)
        self.add_service = add_service or AddService(project)
        self.plugin_url = None

    def get_plugin_url(self):
        discover_json = self.discovery_service.discover_json()
        return discover_json[self.plugin_type].get(self.plugin_name)

    def get_path_to_plugin(self):
        return self.project.venvs_dir(self.plugin_type, self.plugin_name)

    def get_path_to_pip_install(self):
        return self.get_path_to_plugin().joinpath("bin", "pip")

    def create_venv(self):
        self.plugin_url = self.get_plugin_url()

        if not self.plugin_url:
            raise PluginInstallServicePluginNotFoundError()

        return self.venv_service.create(
            namespace=self.plugin_type, name=self.plugin_name
        )

    def install_all_plugins(self, status_cb=None):
        if status_cb is None:
            status_cb = lambda *a, **k: None
        config_yml = self.add_service.meltano_yml
        approved_keys = [
            PluginType.EXTRACTORS,
            PluginType.LOADERS,
        ]
        errors = []
        installed = []
        for kind, plugins in config_yml.items():
            if kind in approved_keys:
                for plugin in plugins:
                    status_cb(
                        {"plugin_type": kind, "plugin": plugin, "status": "running"}
                    )
                    self.plugin_name = plugin.get("name")
                    self.plugin_url = plugin.get("url")
                    self.plugin_type = kind
                    if self.plugin_url is None:
                        errors.append(
                            {
                                "plugin_type": kind,
                                "plugin": plugin,
                                "reason": "Missing URL",
                            }
                        )
                        continue
                    self.create_venv()
                    self.install_plugin()
                    installed.append(
                        {"plugin_type": kind, "plugin": plugin, "status": "success"}
                    )
                    status_cb(
                        {"plugin_type": kind, "plugin": plugin, "status": "success"}
                    )

        return {"errors": errors, "installed": installed}

    def install_plugin(self):
        return self.venv_service.install(
            namespace=self.plugin_type, name=self.plugin_name, pip_url=self.plugin_url
        )
