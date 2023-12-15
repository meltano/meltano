"""Base plugin repository."""

from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod

from meltano.core.plugin.factory import base_plugin_factory

if t.TYPE_CHECKING:
    from meltano.core.plugin import BasePlugin, PluginDefinition, PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin


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
        **kwargs,  # noqa: ANN003
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
