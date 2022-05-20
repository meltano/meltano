"""Meltano Hub Client."""

from __future__ import annotations

import requests

import meltano
from meltano.core.plugin import BasePlugin, PluginDefinition, PluginRef, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_discovery_service import PluginRepository
from meltano.core.project import Project


class MeltanoHubService(PluginRepository):
    """PluginRepository implementation for the Meltano Hub."""

    BASE_URL = "https://hub.meltano.com/meltano/api/v1"

    def __init__(self, project: Project) -> None:
        """Initialize the service.

        Args:
            project: The Meltano project.
        """
        self.project = project
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"Meltano/{meltano.__version__}",
            }
        )

    def plugin_type_endpoint(self, plugin_type: PluginType) -> str:
        """Return the list endpoint for the given plugin type.

        Args:
            plugin_type: The plugin type.

        Returns:
            The endpoint for the given plugin type.
        """
        return f"{self.BASE_URL}/plugins/{plugin_type.value}/index"

    def plugin_endpoint(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> str:
        """Return the resource endpoint for the given plugin.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.

        Returns:
            The endpoint for the given plugin type.
        """
        url = f"{self.BASE_URL}/plugins/{plugin_type.value}/{plugin_name}"
        if variant_name:
            url = f"{url}--{variant_name}"

        return url

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
        url = self.plugin_endpoint(plugin_type, plugin_name, variant_name)
        response = self.session.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            raise PluginNotFoundError(PluginRef(plugin_type, plugin_name)) from err

        return PluginDefinition(**response.json(), plugin_type=plugin_type)

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
