import os
import json
import yaml
import logging
from typing import List

from .project import Project
from .plugin import BasePlugin
from .plugin.project_plugin import ProjectPlugin
from .project_plugins_service import ProjectPluginsService, PluginAlreadyAddedException


class PluginNotSupportedException(Exception):
    pass


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def add(self, *args, **kwargs) -> ProjectPlugin:
        base_plugin = self.plugins_service.discovery_service.find_base_plugin(
            *args, **kwargs
        )
        return self.add_base_plugin(base_plugin)

    def add_base_plugin(self, base_plugin: BasePlugin) -> ProjectPlugin:
        plugin = ProjectPlugin(
            base_plugin.type,
            name=base_plugin.name,
            variant=base_plugin.variant,
            pip_url=base_plugin.pip_url,
        )
        plugin.parent = base_plugin

        return self.add_plugin(plugin)

    def add_plugin(self, plugin: ProjectPlugin):
        return self.plugins_service.add_to_file(plugin)

    def add_related(self, *args, **kwargs):
        related_plugin_refs = self.plugins_service.discovery_service.find_related_plugin_refs(
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
