import os
import yaml
import json
import subprocess

from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.venv_service import VenvService
from .plugin import PluginType
from .project import Project


class PluginInstallService:
    def __init__(
        self,
        project: Project,
        plugin_type=None,
        plugin_name=None,
        discovery_service=None,
        venv_service=None,
        add_service=None,
    ):
        self.project = project
        self._plugin_type = plugin_type
        self._plugin_name = plugin_name
        self.discovery_service = discovery_service or PluginDiscoveryService()
        self.venv_service = venv_service or VenvService(project)
        self.add_service = add_service or ProjectAddService(project)

    @property
    def plugin(self):
        if not self._plugin:
            self._plugin = self.discovery_service.find_plugin(
                self.plugin_type, self.plugin_name
            )
        return self._plugin

    @property
    def plugin_name(self):
        return self._plugin_name

    @plugin_name.setter
    def plugin_name(self, name: str):
        self._plugin = None
        self._plugin_name = name

    @property
    def plugin_type(self):
        return self._plugin_type

    @plugin_type.setter
    def plugin_type(self, type: PluginType):
        self._plugin = None
        self._plugin_type = type

    def get_path_to_plugin(self):
        return self.project.venvs_dir(self.plugin.type, self.plugin.name)

    def get_path_to_pip_install(self):
        return self.get_path_to_plugin().joinpath("bin", "pip")

    def create_venv(self):
        return self.venv_service.create(
            namespace=self.plugin.type, name=self.plugin.name
        )

    def install_all_plugins(self, status_cb=None):
        if status_cb is None:
            status_cb = lambda *a, **k: None

        config_yml = self.add_service.meltano_yml
        approved_keys = [PluginType.EXTRACTORS, PluginType.LOADERS]
        errors = []
        installed = []
        for kind, plugins in config_yml.items():
            if kind in approved_keys:
                for plugin in plugins:
                    status_cb(
                        {"plugin_type": kind, "plugin": plugin, "status": "running"}
                    )
                    self.plugin_name = plugin.get("name")
                    self.plugin_type = kind
                    plugin_url = plugin.get("url")
                    if plugin_url is None:
                        errors.append(
                            {
                                "plugin_type": kind,
                                "plugin": plugin,
                                "reason": "Missing URL",
                            }
                        )
                        continue
                    try:
                        self.create_venv()
                        self.install_plugin(pip_url=plugin_url)
                    except PluginNotFoundError as pnf:
                        errors.append(
                            {
                                "plugin_type": kind,
                                "plugin": plugin,
                                "reason": "Cannot find the plugin.",
                            }
                        )

                    installed.append(
                        {"plugin_type": kind, "plugin": plugin, "status": "success"}
                    )
                    status_cb(
                        {"plugin_type": kind, "plugin": plugin, "status": "success"}
                    )

        return {"errors": errors, "installed": installed}

    def install_plugin(self, pip_url=None):
        install_result = self.venv_service.install(
            namespace=self.plugin.type,
            name=self.plugin.name,
            pip_url=pip_url or self.plugin.pip_url,
        )

        self.install_config_stub()
        return install_result

    def install_config_stub(self):
        plugin_dir = self.project.plugin_dir(self.plugin)
        os.makedirs(plugin_dir, exist_ok=True)

        # TODO: refactor as explicit stubs
        with open(
            plugin_dir.joinpath(self.plugin.config_files["config"]), "w"
        ) as config:
            json.dump(self.plugin.config, config)
