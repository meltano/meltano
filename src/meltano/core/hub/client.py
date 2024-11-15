"""Meltano Hub Client."""

from __future__ import annotations

import typing as t
from http import HTTPStatus

import click
import requests
from requests.adapters import HTTPAdapter
from structlog.stdlib import get_logger
from urllib3 import Retry

import meltano
from meltano.core.hub.schema import IndexedPlugin, VariantRef
from meltano.core.plugin import (
    BasePlugin,
    PluginDefinition,
    PluginRef,
    PluginType,
    Variant,
)
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_repository import PluginRepository

if t.TYPE_CHECKING:
    from meltano.core.project import Project

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
        return (
            f"{self.plugin_type.descriptor.capitalize()} is not supported in "
            f"Meltano Hub. Available plugin types: {PluginType.plurals()}"
        )


class HubConnectionError(Exception):
    """Raised when a Hub connection error occurs."""

    def __init__(self, reason: str):
        """Create a new HubConnectionError.

        Args:
            reason: The reason for the error.
        """
        message = f"Could not connect to Meltano Hub. {reason}"
        super().__init__(message)


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
        return (
            f"{self.plugin_type.descriptor.capitalize()} '{self.plugin.name}' "
            f"variant '{self.variant_name}' is not known to Meltano. "
            f"Variants: {self.plugin.variant_labels}"
        )


class MeltanoHubService(PluginRepository):
    """PluginRepository implementation for the Meltano Hub."""

    session = requests.Session()

    def __init__(self, project: Project) -> None:
        """Initialize the service.

        Args:
            project: The Meltano project.
        """
        self.project = project
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"Meltano/{meltano.__version__}",
            },
        )

        if self.project.settings.get("send_anonymous_usage_stats"):
            project_id = self.project.settings.get("project_id")

            self.session.headers["X-Project-ID"] = project_id

        if self.hub_url_auth:
            self.session.headers.update({"Authorization": self.hub_url_auth})

        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=0,
                status_forcelist=[
                    HTTPStatus.TOO_MANY_REQUESTS,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    HTTPStatus.BAD_GATEWAY,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    HTTPStatus.GATEWAY_TIMEOUT,
                ],
                raise_on_status=False,
            ),
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @property
    def hub_api_url(self) -> str:
        """Return the URL of the Hub API.

        Returns:
            The URL of the Hub API.
        """
        hub_api_root = self.project.settings.get("hub_api_root")
        hub_url = self.project.settings.get("hub_url")

        return hub_api_root or f"{hub_url}/meltano/api/v1"

    @property
    def hub_url_auth(self) -> str:
        """Return the `hub_url_auth` setting.

        Returns:
            The `hub_url_auth` setting.
        """
        return self.project.settings.get("hub_url_auth")

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

    def _build_request(self, method: str, url: str) -> requests.PreparedRequest:
        """Build a request to the Hub API.

        Args:
            method: The HTTP method.
            url: The URL to request.

        Returns:
            The prepared request.
        """
        request = requests.Request(method, url)
        if click_context := click.get_current_context(silent=True):
            request.headers["X-Meltano-Command"] = click_context.command_path

        return self.session.prepare_request(request)

    def _get(self, url: str) -> requests.Response:
        """Make a GET request to the Hub API.

        Args:
            url: The URL to request.

        Returns:
            The response.

        Raises:
            HubConnectionError: If the Hub API could not be reached.
        """
        prep = self._build_request("GET", url)
        settings = self.session.merge_environment_settings(
            prep.url,
            {},
            None,
            None,
            None,
        )

        try:
            return self.session.send(prep, **settings)
        except requests.exceptions.ConnectionError as connection_err:
            raise HubConnectionError("Could not reach Meltano Hub.") from connection_err  # noqa: EM101

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
            HubConnectionError: If the Hub API could not be reached.
        """
        plugins = self.get_plugins_of_type(plugin_type)

        try:
            plugin = plugins[plugin_name]
        except KeyError as plugins_key_err:
            raise PluginNotFoundError(
                PluginRef(plugin_type, plugin_name),
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
                plugin_type,
                plugin,
                variant_name,
            ) from variant_key_err

        response = self._get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            logger.exception(
                "Can not retrieve plugin",
                status_code=http_err.response.status_code,
                error=http_err,
            )
            raise HubConnectionError(str(http_err)) from http_err

        return PluginDefinition(
            **response.json(),
            plugin_type=plugin_type,
            is_default_variant=variant_name == plugin.default_variant,
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

    def get_plugins_of_type(
        self,
        plugin_type: PluginType,
    ) -> dict[str, IndexedPlugin]:
        """Get all plugins of a given type.

        Args:
            plugin_type: The plugin type.

        Returns:
            The plugin definitions.

        Raises:
            HubPluginTypeNotFoundError: If the plugin type is not supported.
            HubConnectionError: If the Hub API could not be reached.
        """
        if not plugin_type.discoverable:
            return {}

        url = self.plugin_type_endpoint(plugin_type)
        response = self._get(url)

        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            logger.exception(
                "Can not retrieve plugin type",
                status_code=err.response.status_code,
                error=err,
            )
            if err.response.status_code < HTTPStatus.TOO_MANY_REQUESTS:
                raise HubPluginTypeNotFoundError(plugin_type) from err
            raise HubConnectionError(err.response.reason) from err

        plugins: dict[str, dict[str, t.Any]] = response.json()
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
