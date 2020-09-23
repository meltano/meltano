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

    def add(self, plugin_type: PluginType, plugin_name: str, **kwargs) -> ProjectPlugin:
        plugin_def = self.discovery_service.find_plugin(plugin_type, plugin_name)
        project_plugin = plugin_def.in_project()
        return self.config_service.add_to_file(project_plugin)

    def add_custom(self, plugin_def: PluginDefinition) -> ProjectPlugin:
        project_plugin = plugin_def.in_project(custom=True)
        return self.config_service.add_to_file(project_plugin)

    def add_related(
        self,
        target_plugin: ProjectPlugin,
        plugin_types: List[PluginType] = list(PluginType),
    ):
        try:
            plugin_types.remove(target_plugin.type)
        except ValueError:
            pass

        related_plugin_refs = []

        runner_ref = target_plugin.runner
        if runner_ref:
            related_plugin_refs.append(runner_ref)

        plugin_def = self.discovery_service.find_plugin(
            target_plugin.type, target_plugin.name
        )
        related_plugin_refs.extend(
            related_plugin_def
            for plugin_type in plugin_types
            for related_plugin_def in self.discovery_service.get_plugins_of_type(
                plugin_type
            )
            if related_plugin_def.namespace == plugin_def.namespace
        )

        added_plugins = []
        for plugin_ref in related_plugin_refs:
            try:
                project_plugin = self.add(plugin_ref.type, plugin_ref.name)
            except PluginAlreadyAddedException as err:
                continue

            added_plugins.append(project_plugin)

        added_plugins_with_related = []
        for project_plugin in added_plugins:
            added_plugins_with_related.extend(
                [
                    project_plugin,
                    *self.add_related(project_plugin, plugin_types=plugin_types),
                ]
            )

        return added_plugins_with_related
