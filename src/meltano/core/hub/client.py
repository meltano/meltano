"""Meltano Hub Client."""

from __future__ import annotations

import sys
import typing as t
from contextlib import suppress
from http import HTTPStatus

import click
import requests
import requests.exceptions
from requests.adapters import HTTPAdapter
from structlog.stdlib import get_logger
from urllib3 import Retry

from meltano.core.error import MeltanoError
from meltano.core.hub.schema import IndexedPlugin, VariantRef
from meltano.core.plugin import PluginDefinition, PluginRef, PluginType, Variant
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_repository import PluginRepository

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from meltano.core.cloud.credentials import Credentials
    from meltano.core.plugin import BasePlugin
    from meltano.core.project import Project

logger = get_logger(__name__)


def _rejection_detail(response: requests.Response) -> str | None:
    """Read the Hub's own explanation out of a rejected response.

    Letting the Hub supply the wording means it can be changed server side,
    without waiting for users to upgrade Meltano.

    Args:
        response: The rejected response.

    Returns:
        The explanation, or `None` if the Hub did not give a useful one.
    """
    try:
        message = response.json().get("message")
    except ValueError:
        return None

    if not isinstance(message, str) or not message.strip():
        return None

    # The error renders the reason with a full stop after it, so drop the
    # Hub's own, rather than requiring it to know how Meltano punctuates.
    return message.strip().removesuffix(".") or None


def _connection_cause(error: requests.exceptions.ConnectionError) -> str | None:
    """Pull the underlying cause out of a `requests` connection error.

    The error's own string form repeats the URL and buries the cause under two
    layers of pool machinery, so read the cause that urllib3 recorded instead.

    Args:
        error: The connection error.

    Returns:
        The cause, or `None` if urllib3 did not record one.
    """
    retry_error = error.args[0] if error.args else None
    reason = getattr(retry_error, "reason", None)
    if reason is None:
        return None

    # urllib3 usually prefixes the cause with a repr of the connection it
    # attempted. Strip that alone, so an unprefixed cause survives intact.
    text = str(reason)
    prefix, separator, rest = text.partition(": ")
    if separator and prefix.endswith(")") and "Connection(" in prefix:
        text = rest
    return text.strip() or None


class HubPluginTypeNotFoundError(MeltanoError):
    """Raised when a Hub plugin type is not found."""

    def __init__(self, plugin_type: PluginType):
        """Create a new HubPluginVariantNotFound.

        Args:
            plugin_type: The type of the plugin.
        """
        self.plugin_type = plugin_type
        super().__init__(
            f"{self.plugin_type.descriptor.capitalize()} is not supported in "
            f"Meltano Hub. Available plugin types: {PluginType.plurals()}"
        )


class HubConnectionError(MeltanoError):
    """Raised when a Hub connection error occurs."""

    def __init__(self, reason: str | None = None):
        """Create a new HubConnectionError.

        Args:
            reason: The reason for the error.
        """
        super().__init__(reason or "Could not connect to Meltano Hub")


class HubAuthenticationRequiredError(MeltanoError):
    """Raised when Meltano Hub rejects a request as unauthenticated."""

    # Always set, unlike the base class, so a caller can add to it.
    instruction: str

    def __init__(self, status_code: int, detail: str | None = None):
        """Create a new HubAuthenticationRequiredError.

        Args:
            status_code: The status code returned by the Hub API.
            detail: The Hub's own explanation, when it gave one.
        """
        super().__init__(
            detail or f"Meltano Hub requires authentication ({status_code})",
            "Run 'meltano cloud auth login' to log in or register for Meltano Cloud",
        )


class HubPluginVariantNotFoundError(MeltanoError):
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
        super().__init__(
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
                "User-Agent": project.user_agent,
            },
        )

        if self.project.settings.get("send_anonymous_usage_stats"):
            project_id = self.project.settings.get("project_id")

            self.session.headers["X-Project-ID"] = project_id

        self.session.headers.pop("Authorization", None)
        if self.hub_url_auth:
            self.session.headers.update({"Authorization": self.hub_url_auth})
        elif credentials := self._cloud_credentials():
            self.session.headers.update(credentials.auth_header)

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
        """The URL of the Hub API."""
        hub_api_root = self.project.settings.get("hub_api_root")
        hub_url = self.project.settings.get("hub_url")

        return hub_api_root or f"{hub_url}/meltano/api/v1"

    @property
    def hub_url_auth(self) -> str | None:
        """The `hub_url_auth` setting."""
        return self.project.settings.get("hub_url_auth")

    @staticmethod
    def _cloud_credentials() -> Credentials | None:
        """Get the stored Meltano Cloud session, renewing it if it has expired.

        Returns:
            The credentials, or `None` if the user is not logged in.
        """
        # Imported here so that fetching a plugin definition does not pay for
        # the login flow's HTTP server and browser launcher.
        from meltano.core.cloud.auth import CloudAuthService
        from meltano.core.user_config import UserConfigReadError

        # A user configuration file that cannot be read must not stop a plugin
        # being added, so treat it as being logged out.
        with suppress(UserConfigReadError):
            return CloudAuthService().get_credentials()

        return None

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
            request.headers["X-Meltano-Command"] = click_context.command_path  # type: ignore[index] # ty:ignore[invalid-assignment]

        return self.session.prepare_request(request)

    def _get(self, url: str) -> requests.Response:
        """Make a GET request to the Hub API.

        Args:
            url: The URL to request.

        Returns:
            The response.

        Raises:
            HubConnectionError: If the Hub API could not be reached.
            HubAuthenticationRequiredError: If the Hub API rejected the request
                because the user is not logged in to Meltano Cloud.
        """
        prep = self._build_request("GET", url)
        settings = self.session.merge_environment_settings(
            prep.url,  # type: ignore[arg-type] # ty:ignore[invalid-argument-type]
            {},
            None,
            None,
            None,
        )

        try:
            response = self.session.send(prep, **settings)
        except requests.exceptions.ConnectionError as connection_err:
            reason = f"Could not connect to Meltano Hub at {url}"
            if cause := _connection_cause(connection_err):
                reason = f"{reason}: {cause}"
            raise HubConnectionError(reason) from connection_err

        # A project that sets 'hub_url_auth' manages its own credentials, so
        # report the status instead of the Cloud login.
        if response.status_code == HTTPStatus.UNAUTHORIZED and not self.hub_url_auth:
            raise HubAuthenticationRequiredError(
                response.status_code,
                _rejection_detail(response),
            )

        return response

    @override
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
        try:
            plugin = self.get_plugins_of_type(plugin_type)[plugin_name]
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

        logger.info("Fetching plugin definition from Meltano Hub", url=url)
        response = self._get(url)

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            reason = (
                f"{response.reason or 'Unknown reason'} ({response.status_code}): "
                "can not retrieve plugin"
            )
            raise HubConnectionError(reason)

        return PluginDefinition(
            **response.json(),
            plugin_type=plugin_type,
            is_default_variant=variant_name == plugin.default_variant,
        )

    @override
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

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise HubPluginTypeNotFoundError(plugin_type)

        if response.status_code >= HTTPStatus.BAD_REQUEST:
            reason = (
                f"{response.reason or 'Unknown reason'} ({response.status_code}): "
                f"can not retrieve plugins of type '{plugin_type.singular}'"
            )
            raise HubConnectionError(reason)

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
