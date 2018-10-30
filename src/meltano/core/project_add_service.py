import os
import json
import yaml
import logging

from .project import Project
from .plugin import PluginType, Plugin
from .plugin_discovery_service import PluginDiscoveryService
from .config_service import ConfigService


class PluginNotSupportedException(Exception):
    pass


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(
        self, project: Project,
        discovery_service: PluginDiscoveryService = None,
        config_service: ConfigService = None
    ):
        self.project = project
        self.discovery_service = discovery_service or PluginDiscoveryService()
        self.config_service = config_service or ConfigService(project)

        try:
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}
        except Exception as e:
            self.project.meltanofile.open("a").close()
            self.meltano_yml = yaml.load(open(self.project.meltanofile)) or {}

    def add(self, plugin_type: PluginType, plugin_name: str):
        plugin = self.discovery_service.find_plugin(plugin_type, plugin_name)

        extract_dict = self.meltano_yml.get(plugin_type)
        if not extract_dict:
            self.meltano_yml[plugin.type] = []
            extract_dict = self.meltano_yml.get(plugin.type)

        if plugin.pip_url:
            self.add_to_file(plugin)
        else:
            raise PluginNotSupportedException()

        return plugin

    def add_to_file(self, plugin: Plugin):
        if plugin in self.config_service.plugins():
            logging.warn(
                f"{plugin.name} is already present, use `meltano install` to install it."
            )
            return

        self.meltano_yml[plugin.type].append(plugin.canonical())
        with open(self.project.meltanofile, "w") as f:
            f.write(yaml.dump(self.meltano_yml, default_flow_style=False))
