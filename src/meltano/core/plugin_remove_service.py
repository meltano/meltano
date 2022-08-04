"""Defines PluginRemoveService."""

from __future__ import annotations

from typing import Iterable

from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_location_remove import (
    DbRemoveManager,
    InstallationRemoveManager,
    LockedDefinitionRemoveManager,
    MeltanoYmlRemoveManager,
    PluginLocationRemoveManager,
)
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project
from .utils import noop


class PluginRemoveService:
    """Handle plugin installation removal operations."""

    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        """Construct a PluginRemoveService instance.

        Args:
            project: The Meltano project.
            plugins_service: The project plugins service.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def remove_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
        plugin_status_cb=noop,
        removal_manager_status_cb=noop,
    ) -> tuple[int, int]:
        """
        Remove multiple plugins.

        Returns a tuple containing:
        1. The total number of removed plugins
        2. The total number of plugins attempted

        Args:
            plugins: The plugins to remove.
            plugin_status_cb: A callback to call for each plugin.
            removal_manager_status_cb: A callback to call for each removal manager.

        Returns:
            A tuple containing:
            1. The total number of removed plugins
            2. The total number of plugins attempted
        """
        num_plugins: int = len(plugins)
        removed_plugins: int = num_plugins

        for plugin in plugins:
            plugin_status_cb(plugin)

            removal_managers = self.remove_plugin(plugin)

            any_not_removed = False
            for manager in removal_managers:
                any_not_removed = not manager.plugin_removed or any_not_removed
                removal_manager_status_cb(manager)

            if any_not_removed:
                removed_plugins -= 1

        return removed_plugins, num_plugins

    def remove_plugin(
        self, plugin: ProjectPlugin
    ) -> tuple[PluginLocationRemoveManager]:
        """Remove a plugin.

        Removes from `meltano.yml`, its installation in `.meltano`, and its settings in
        the Meltano system database.

        Args:
            plugin: The plugin to remove.

        Returns:
            A tuple containing a remove manager for each location.
        """
        remove_managers = (
            DbRemoveManager(plugin, self.project),
            MeltanoYmlRemoveManager(plugin, self.project),
            InstallationRemoveManager(plugin, self.project),
            LockedDefinitionRemoveManager(plugin, self.project),
        )

        for manager in remove_managers:
            manager.remove()

        return remove_managers
