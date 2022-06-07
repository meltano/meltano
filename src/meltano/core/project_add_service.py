"""Add plugins to the project."""

from __future__ import annotations

import enum
from typing import Iterable

from .plugin import BasePlugin, PluginType, Variant
from .plugin.project_plugin import ProjectPlugin
from .project import Project
from .project_plugins_service import PluginAlreadyAddedException, ProjectPluginsService


class PluginAddedReason(str, enum.Enum):
    """The reason why a plugin was added to the project."""

    #: The plugin was added by the user.
    USER_REQUEST = "user_request"

    #: The plugin was added because it is related to another plugin.
    RELATED = "related"

    #: The plugin was added because it is required by another plugin.
    REQUIRED = "required"


class MissingPluginException(Exception):
    """Raised when a plugin is not found."""


class ProjectAddService:
    """Project Add Service."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
    ):
        """Create a new Project Add Service.

        Args:
            project: The project to add plugins to.
            plugins_service: The project plugins service.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def add(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        lock: bool = True,
        **attrs,
    ) -> ProjectPlugin:
        """Add a new plugin to the project.

        Args:
            plugin_type: The type of the plugin to add.
            plugin_name (str): The name of the plugin to add.
            lock: Whether to generate a lockfile for the plugin.
            attrs: Additional attributes to add to the plugin.

        Returns:
            The added plugin.
        """
        plugin = ProjectPlugin(
            plugin_type, plugin_name, **attrs, default_variant=Variant.DEFAULT_NAME
        )

        with self.plugins_service.disallow_discovery_yaml():
            self.plugins_service.ensure_parent(plugin)

            # If we are inheriting from a base plugin definition,
            # repeat the variant and pip_url in meltano.yml
            parent = plugin.parent
            if isinstance(parent, BasePlugin):
                # raise
                plugin.variant = parent.variant
                plugin.pip_url = parent.pip_url

            added = self.add_plugin(plugin)

            if lock and not added.is_custom():
                self.plugins_service.lock_service.save(
                    added,
                    exists_ok=plugin.inherit_from is not None,
                )

            return added

    def add_plugin(self, plugin: ProjectPlugin):
        """Add a plugin to the project.

        Args:
            plugin: The plugin to add.

        Returns:
            The added plugin.
        """
        return self.plugins_service.add_to_file(plugin)

    def add_related(self, *args, **kwargs):
        """Add all related plugins to the project.

        Args:
            args: The plugin type and name of the plugin to add.
            kwargs: Additional attributes to add to the plugin.

        Returns:
            The added plugins.
        """
        related_plugin_refs = (
            self.plugins_service.discovery_service.find_related_plugin_refs(
                *args, **kwargs
            )
        )

        added_plugins = []
        for plugin_ref in related_plugin_refs:
            try:
                plugin = self.add(plugin_ref.type, plugin_ref.name)
            except PluginAlreadyAddedException:
                continue

            added_plugins.append(plugin)

        added_plugins_with_related = []
        for added in added_plugins:
            added_plugins_with_related.extend(
                [added, *self.add_related(added, **kwargs)]
            )

        return added_plugins_with_related

    def add_required(
        self,
        plugin: ProjectPlugin,
        plugin_types: Iterable[PluginType] | None = None,
    ):
        """Add all required plugins to the project.

        Args:
            plugin: The plugin to get requirements from.
            plugin_types: The plugin types to add.

        Returns:
            The added plugins.
        """
        plugin_types = plugin_types or list(PluginType)

        try:
            plugin_types.remove(plugin.type)
        except ValueError:
            pass

        added_plugins = []
        for plugin_type, plugins in plugin.get_requirements(plugin_types).items():
            for plugin_req in plugins:
                try:
                    plugin = self.add(
                        plugin_type,
                        plugin_req.name,
                        variant=plugin_req.variant,
                    )
                except PluginAlreadyAddedException:
                    continue

                added_plugins.append(plugin)

        added_plugins_with_required = []
        for added in added_plugins:
            added_plugins_with_required.extend([added, *self.add_required(added)])

        return added_plugins_with_required
