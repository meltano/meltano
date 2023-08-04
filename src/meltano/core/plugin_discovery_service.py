"""Discover plugin definitions."""

from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod
from glob import iglob

from meltano.core.plugin import BasePlugin, PluginDefinition, PluginRef, PluginType
from meltano.core.plugin.base import StandalonePlugin
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin.project_plugin import ProjectPlugin

if t.TYPE_CHECKING:
    from meltano.core.project import Project

REQUEST_TIMEOUT_SECONDS = 30.0


class PluginRepository(metaclass=ABCMeta):
    """A generic plugin definition repository."""

    @abstractmethod
    def find_definition(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> PluginDefinition:
        """Find a plugin definition.

        Args:
            plugin_type: The type of plugin to find.
            plugin_name: The name of the plugin to find.
            variant_name: The name of the variant to find.
        """

    def find_base_plugin(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant: str | None = None,
    ) -> BasePlugin:
        """Get the base plugin for a project plugin.

        Args:
            plugin_type: The type of plugin to get the base plugin for.
            plugin_name: The name of the plugin to get the base plugin for.
            variant: The variant of the plugin to get the base plugin for.

        Returns:
            The base plugin.
        """
        plugin = self.find_definition(
            plugin_type,
            plugin_name,
        )

        return base_plugin_factory(plugin, variant)

    def get_base_plugin(
        self,
        project_plugin: ProjectPlugin,
        **kwargs,
    ) -> BasePlugin:
        """Get the base plugin for a project plugin.

        Args:
            project_plugin: The project plugin to get the base plugin for.
            kwargs: Additional arguments to pass to the finder.

        Returns:
            The base plugin.
        """
        plugin = project_plugin.custom_definition or self.find_definition(
            project_plugin.type,
            project_plugin.inherit_from or project_plugin.name,
            **kwargs,
        )

        return base_plugin_factory(plugin, project_plugin.variant)


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
        path = self.project.plugin_lock_path(plugin_type, plugin_name, variant_name)
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
    ) -> t.Iterable[PluginDefinition]:
        """Get all plugin definitions of a given type.

        Args:
            plugin_type: The plugin type.

        Yields:
            Locked plugin definitions for the given type.
        """
        yield from (
            PluginDefinition.from_standalone(
                StandalonePlugin.parse_json_file(lockfile),  # type: ignore[arg-type]
            )
            for lockfile in iglob(
                "*.lock",
                root_dir=self.project.root_plugins_dir(plugin_type.value),
            )
        )
