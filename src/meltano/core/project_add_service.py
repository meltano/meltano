import os
import json
import yaml
import logging
from typing import List

from .project import Project
from .plugin import PluginType, PluginDefinition, ProjectPlugin, PluginRef
from .plugin_discovery_service import PluginDiscoveryService
from .plugin.factory import plugin_factory
from .config_service import ConfigService, PluginAlreadyAddedException


class PluginNotSupportedException(Exception):
    pass


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

    def add(self, *args, **kwargs) -> ProjectPlugin:
        plugin_def = self.discovery_service.find_definition(*args, **kwargs)
        return self.add_definition(plugin_def)

    def add_definition(self, plugin_def: PluginDefinition) -> ProjectPlugin:
        plugin = ProjectPlugin(
            plugin_def.type,
            name=plugin_def.name,
            variant=plugin_def.current_variant_name,
            pip_url=plugin_def.pip_url,
        )

        return self.add_plugin(plugin)

    def add_plugin(self, plugin: ProjectPlugin):
        return self.config_service.add_to_file(plugin)

    def add_related(self, *args, **kwargs):
        related_plugin_refs = self.discovery_service.find_related_plugin_refs(
            *args, **kwargs
        )

        added_plugins = []
        for plugin_ref in related_plugin_refs:
            try:
                plugin = self.add(plugin_ref.type, plugin_ref.name)
            except PluginAlreadyAddedException as err:
                continue

            added_plugins.append(plugin)

        added_plugins_with_related = []
        for plugin in added_plugins:
            added_plugins_with_related.extend(
                [plugin, *self.add_related(plugin, **kwargs)]
            )

        return added_plugins_with_related
