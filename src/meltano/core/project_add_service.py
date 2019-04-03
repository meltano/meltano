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


class PluginAlreadyAddedException(Exception):
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        super().__init__()


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    EXTRACTOR = "extractor"
    LOADER = "loader"

    def __init__(
        self,
        project: Project,
        plugin_discovery_service: PluginDiscoveryService = None,
        config_service: ConfigService = None,
    ):
        self.project = project
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self.config_service = config_service or ConfigService(project)

    def add(self, plugin_type: PluginType, plugin_name: str, **kwargs):
        plugin = self.discovery_service.find_plugin(plugin_type, plugin_name)

        with self.project.meltano_update() as meltano_yml:
            meltano_yml["plugins"] = meltano_yml.get("plugins", {})
            meltano_yml["plugins"][plugin_type] = meltano_yml["plugins"].get(
                plugin_type, []
            )

        if plugin.pip_url:
            self.add_to_file(plugin, **kwargs)
        else:
            raise PluginNotSupportedException()

        return plugin

    def add_to_file(self, plugin: Plugin, exists_ok=False):
        if plugin in self.config_service.plugins():
            if not exists_ok:
                raise PluginAlreadyAddedException(plugin)
            return

        with self.project.meltano_update() as meltano_yml:
            meltano_yml["plugins"][plugin.type].append(plugin.canonical())
