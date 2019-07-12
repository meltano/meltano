import os
import json
import yaml
import logging

from .project import Project
from .plugin import PluginType, PluginInstall, PluginRef
from .plugin_discovery_service import PluginDiscoveryService
from .plugin.factory import plugin_factory
from .config_service import ConfigService


class PluginNotSupportedException(Exception):
    pass


class PluginAlreadyAddedException(Exception):
    def __init__(self, plugin: PluginRef):
        self.plugin = plugin
        super().__init__()


class MissingPluginException(Exception):
    pass


class ProjectAddService:
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

    def add(self, plugin_type: PluginType, plugin_name: str, **kwargs) -> PluginInstall:
        plugin = self.discovery_service.find_plugin(plugin_type, plugin_name)
        installed = plugin.as_installed()
        return self.config_service.add_to_file(installed)
