"""Locked plugin definition service."""

from __future__ import annotations

import typing as t

from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_lock_service import PluginLockService
from meltano.core.plugin_repository import PluginRepository

if t.TYPE_CHECKING:
    from meltano.core.plugin import BasePlugin, PluginDefinition, PluginType
    from meltano.core.project import Project


class LockedDefinitionService(PluginRepository):
    """PluginRepository implementation for local files."""

    def __init__(self, project: Project) -> None:
        """Initialize the service.

        Args:
            project: The Meltano project.
        """
        self.project = project
        self.lock_service = PluginLockService(project)

    def find_definition(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> PluginDefinition:
        """Find a locked plugin definition.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.

        Returns:
            The plugin definition.

        Raises:
            PluginNotFoundError: If the plugin definition could not be found.
        """
        return self.lock_service.load_definition(
            plugin_type=plugin_type,
            plugin_name=plugin_name,
            variant_name=variant_name,
        )

    def find_base_plugin(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant: str | None = None,
    ) -> BasePlugin:
        """Get the base plugin for a project plugin.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant: The plugin variant.

        Returns:
            The base plugin.
        """
        plugin = self.find_definition(
            plugin_type,
            plugin_name,
            variant_name=variant,
        )

        return base_plugin_factory(plugin, plugin.variants[0])
