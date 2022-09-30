"""Meltano Hub Client."""

from __future__ import annotations

from typing import Any

import requests
from structlog.stdlib import get_logger

import meltano
from meltano.core.plugin import (
    BasePlugin,
    PluginDefinition,
    PluginRef,
    PluginType,
    Variant,
)
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_discovery_service import PluginRepository
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService

from .schema import IndexedPlugin, VariantRef

logger = get_logger(__name__)


class HubPluginTypeNotFoundError(Exception):
    """Raised when a Hub plugin type is not found."""

    def __init__(self, plugin_type: PluginType):
        """Create a new HubPluginVariantNotFound.

        Args:
            plugin_type: The type of the plugin.
        """
        self.plugin_type = plugin_type

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            The string representation of the error.
        """
        return "{type} is not supported in Meltano Hub. Available plugin types: {types}".format(
            type=self.plugin_type.descriptor.capitalize(),
            types=list(PluginType),
        )


class HubPluginVariantNotFoundError(Exception):
    """Raised when a Hub plugin variant is not found."""

    def __init__(
        self,
        plugin_type: PluginType,
        plugin: IndexedPlugin,
        variant_name: str,
    ):
        """Create a new HubPluginVariantNotFound.

        Args:
            plugin_type: The type of the plugin.
            plugin: The indexed plugin.
            variant_name: The name of the variant that was not found.
        """
        self.plugin_type = plugin_type
        self.plugin = plugin
        self.variant_name = variant_name

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            The string representation of the error.
        """
        return "{type} '{name}' variant '{variant}' is not known to Meltano. Variants: {variant_labels}".format(
            type=self.plugin_type.descriptor.capitalize(),
            name=self.plugin.name,
            variant=self.variant_name,
            variant_labels=self.plugin.variant_labels,
        )


class MeltanoHubService(PluginRepository):
    """PluginRepository implementation for the Meltano Hub."""

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

        self.settings_service = ProjectSettingsService(self.project)

        if self.settings_service.get("send_anonymous_usage_stats"):
            project_id = self.settings_service.get("project_id")

            self.session.headers["X-Project-ID"] = project_id

        if self.hub_url_auth:
            self.session.headers.update({"Authorization": self.hub_url_auth})

    @property
    def hub_api_url(self):
        """Return the URL of the Hub API.

        Returns:
            The URL of the Hub API.
        """
        hub_api_root = self.settings_service.get("hub_api_root")
        hub_url = self.settings_service.get("hub_url")

        return hub_api_root or f"{hub_url}/meltano/api/v1"

    @property
    def hub_url_auth(self):
        """Return the `hub_url_auth` setting.

        Returns:
            The `hub_url_auth` setting.
        """
        return self.settings_service.get("hub_url_auth")

    def plugin_type_endpoint(self, plugin_type: PluginType) -> str:
        """Return the list endpoint for the given plugin type.

        Args:
            plugin_type: The plugin type.

        Returns:
            The endpoint for the given plugin type.
        """
        return f"{self.hub_api_url}/plugins/{plugin_type.value}/index"

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
        url = f"{self.hub_api_url}/plugins/{plugin_type.value}/{plugin_name}"
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
            HubPluginVariantNotFoundError: If the plugin variant could not be found.
        """
        plugins = self.get_plugins_of_type(plugin_type)

        try:
            plugin = plugins[plugin_name]
        except KeyError as plugins_key_err:
            raise PluginNotFoundError(
                PluginRef(plugin_type, plugin_name)
            ) from plugins_key_err

        if variant_name is None or variant_name in {
            Variant.DEFAULT_NAME,
            Variant.ORIGINAL_NAME,
        }:
            variant_name = plugin.default_variant

        try:
            url = plugin.variants[variant_name].ref
        except KeyError as variant_key_err:
            raise HubPluginVariantNotFoundError(
                plugin_type, plugin, variant_name
            ) from variant_key_err

        response = self.session.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            logger.error(
                "Can not retrieve plugin",
                status_code=http_err.response.status_code,
                error=http_err,
            )
            raise PluginNotFoundError(PluginRef(plugin_type, plugin_name)) from http_err

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

    def get_plugins_of_type(self, plugin_type: PluginType) -> dict[str, IndexedPlugin]:
        """Get all plugins of a given type.

        Args:
            plugin_type: The plugin type.

        Returns:
            The plugin definitions.

        Raises:
            HubPluginTypeNotFoundError: If the plugin type is not supported.
        """
        if not plugin_type.discoverable:
            return {}

        url = self.plugin_type_endpoint(plugin_type)
        response = self.session.get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            logger.error(
                "Can not retrieve plugin type",
                status_code=err.response.status_code,
                error=err,
            )
            raise HubPluginTypeNotFoundError(plugin_type) from err

        plugins: dict[str, dict[str, Any]] = response.json()
        return {
            name: IndexedPlugin(
                name,
                logo_url=plugin["logo_url"],
                default_variant=plugin["default_variant"],
                variants={
                    variant_name: VariantRef(variant_name, ref=variant["ref"])
                    for variant_name, variant in plugin["variants"].items()
                },
            )
            for name, plugin in plugins.items()
        }
