import json
import logging
import os
from typing import List

import yaml

from .plugin import BasePlugin, PluginType, Variant
from .plugin.project_plugin import ProjectPlugin
from .project import Project
from .project_plugins_service import PluginAlreadyAddedException, ProjectPluginsService


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def add(self, plugin_type: PluginType, plugin_name: str, **attrs) -> ProjectPlugin:
        """Add plugin to project."""
        plugin = ProjectPlugin(
            plugin_type, plugin_name, **attrs, default_variant=Variant.DEFAULT_NAME
        )

        self.plugins_service.ensure_parent(plugin)

        # If we are inheriting from a base plugin definition,
        # repeat the variant and pip_url in meltano.yml
        parent = plugin.parent
        if isinstance(parent, BasePlugin):
            plugin.variant = parent.variant
            plugin.pip_url = parent.pip_url

        return self.add_plugin(plugin)

    def add_plugin(self, plugin: ProjectPlugin):
        return self.plugins_service.add_to_file(plugin)

    def add_related(self, *args, **kwargs):
        related_plugin_refs = (
            self.plugins_service.discovery_service.find_related_plugin_refs(
                *args, **kwargs
            )
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
