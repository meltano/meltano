"""Locked plugin definition service."""

from __future__ import annotations

import typing as t

from meltano.core.plugin import BasePlugin, PluginDefinition, PluginRef, PluginType
from meltano.core.plugin.base import StandalonePlugin
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_repository import PluginRepository

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from meltano.core.project import Project


class LockedDefinitionService(PluginRepository):
    """PluginRepository implementation for local files."""

    def __init__(self, project: Project) -> None:
        """Initialize the service.

        Args:
            project: The Meltano project.
        """
        self.project = project

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
        path = self.project.plugin_lock_path(
            plugin_type,
            plugin_name,
            variant_name=variant_name,
        )
        try:
            standalone = StandalonePlugin.parse_json_file(path)
        except FileNotFoundError as err:
            raise PluginNotFoundError(PluginRef(plugin_type, plugin_name)) from err
        return PluginDefinition.from_standalone(standalone)

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

    def get_plugins_of_type(
        self,
        plugin_type: PluginType,
    ) -> Iterable[PluginDefinition]:
        """Get all plugin definitions of a given type.

        Args:
            plugin_type: The plugin type.

        Yields:
            Locked plugin definitions for the given type.
        """
        plugin_type_dir = self.project.root_plugins_dir(plugin_type.value)
        yield from (
            PluginDefinition.from_standalone(StandalonePlugin.parse_json_file(lockfile))
            for lockfile in plugin_type_dir.glob("*.lock")
        )
