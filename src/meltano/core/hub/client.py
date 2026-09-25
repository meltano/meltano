"""Meltano Hub Client."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import typing as t
from contextlib import contextmanager, suppress
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import click
import platformdirs
import requests
import requests.exceptions
from requests.adapters import HTTPAdapter
from structlog.stdlib import get_logger
from urllib3 import Retry

from meltano.core.cloud.config import CLOUD_API_ROOT
from meltano.core.error import MeltanoError
from meltano.core.hub.schema import IndexedPlugin, VariantRef
from meltano.core.plugin import PluginDefinition, PluginRef, PluginType, Variant
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin_repository import PluginRepository
from meltano.core.settings_store import SettingValueStore

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.cloud.credentials import Credentials
    from meltano.core.plugin import BasePlugin
    from meltano.core.project import Project

logger = get_logger(__name__)

# How long an index of a plugin type is reused before it is fetched again.
INDEX_CACHE_DURATION = timedelta(hours=1)


def index_cache_dir() -> Path:
    """Get the directory that caches an index of a plugin type."""
    return platformdirs.user_cache_path("meltano") / "hub"


def _index_cache_path(url: str) -> Path:
    """Get the file that caches the index at a URL.

    Args:
        url: The index URL, which a project can point elsewhere.

    Returns:
        The path of the cache file.
    """
    return index_cache_dir() / f"{hashlib.sha256(url.encode()).hexdigest()}.json"


def _read_index_cache(path: Path) -> dict[str, t.Any] | None:
    """Read an index that was cached, if it is still fresh.

    Args:
        path: The path of the cache file.

    Returns:
        The index, or `None` if it was never cached or has expired.
    """
    if not path.exists():
        return None

    written = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    if datetime.now(tz=timezone.utc) - written > INDEX_CACHE_DURATION:
        return None

    return json.loads(path.read_text())


def _write_index_cache(path: Path, index: dict[str, t.Any]) -> None:
    """Cache an index.

    The file is renamed into place, so that a run which is interrupted part way
    through writing it leaves no half-written file for the next one to read.

    Args:
        path: The path of the cache file.
        index: The index to cache.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(f".{os.getpid()}.partial")
    partial.write_text(json.dumps(index))
    os.replace(partial, path)  # noqa: PTH105


def _rejection_detail(response: requests.Response) -> str | None:
    """Read the Hub's own explanation out of a rejected response.

    Letting the Hub supply the wording means it can be changed server side,
    without waiting for users to upgrade Meltano.

    Args:
        response: The rejected response.

    Returns:
        The explanation, or `None` if the Hub sent no JSON message.
    """
    try:
        message = response.json()["message"]
    except (ValueError, KeyError):
        return None

    # The error renders the reason with a full stop after it, so drop the
    # Hub's own, rather than requiring it to know how Meltano punctuates.
    return message.strip().removesuffix(".") or None


def _connection_cause(error: requests.exceptions.ConnectionError) -> str | None:
    """Pull the underlying cause out of a `requests` connection error.

    The error's own string form repeats the URL and buries the cause under two
    layers of pool machinery, so read the error that urllib3 chained instead.

    Args:
        error: The connection error.

    Returns:
        The cause, or `None` if urllib3 did not record one.
    """
    reason = getattr(error.args[0] if error.args else None, "reason", None)
    if reason is None:
        return None

    # A TLS failure carries its own message rather than chaining an OSError.
    return str(reason.__cause__ or reason)


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

    def __init__(self, detail: str | None = None):
        """Create a new HubAuthenticationRequiredError.

        Args:
            detail: The Hub's own explanation, when it gave one.
        """
        super().__init__(
            detail or "Meltano Hub requires authentication",
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


@contextmanager
def _cloud_login_hint() -> t.Iterator[None]:
    """Print the hint after the command output, where a long output cannot bury it.

    A failed command skips the hint, so that the error stays the last line.
    """
    yield  # noqa: RUF075
    click.secho(
        "Run 'meltano cloud auth login' to get supported plugins from Meltano Cloud",
        fg="bright_yellow",
        err=True,
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
        self.cloud_authenticated = False
        if self.hub_url_auth:
            self.session.headers.update({"Authorization": self.hub_url_auth})
        elif credentials := self.cloud_credentials():
            self.session.headers.update(credentials.auth_header)
            self.cloud_authenticated = True

        if (
            not self.cloud_authenticated
            and not self.has_configured_hub
            and (click_context := click.get_current_context(silent=True))
        ):
            click_context.with_resource(_cloud_login_hint())

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
    def has_configured_hub(self) -> bool:
        """Whether the project points Meltano at a Hub of its own."""
        if self.project.settings.get("hub_api_root") or self.hub_url_auth:
            return True

        _, source = self.project.settings.get_with_source("hub_url")
        return source is not SettingValueStore.DEFAULT

    @property
    def hub_api_url(self) -> str:
        """The URL of the Hub API."""
        if hub_api_root := self.project.settings.get("hub_api_root"):
            return hub_api_root

        # A logged in user reads the index that Meltano Cloud serves, which
        # lists the plugins that Meltano supports, maintains and tests. A
        # project that points 'hub_url' at a Hub of its own keeps that one.
        if self.cloud_authenticated and not self.has_configured_hub:
            return CLOUD_API_ROOT

        hub_url = self.project.settings.get("hub_url")
        return f"{hub_url}/meltano/api/v1"

    @property
    def hub_url_auth(self) -> str | None:
        """The `hub_url_auth` setting."""
        return self.project.settings.get("hub_url_auth")

    @staticmethod
    def cloud_credentials() -> Credentials | None:
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
            raise HubAuthenticationRequiredError(_rejection_detail(response))

        return response

    @override
    def find_definition(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
        *,
        refresh: bool = True,
    ) -> PluginDefinition:
        """Find a locked plugin definition.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.
            refresh: Whether to fetch the index and the definition rather than
                reuse ones cached in the last `INDEX_CACHE_DURATION`.

        Returns:
            The plugin definition.

        Raises:
            PluginNotFoundError: If the plugin definition could not be found.
            HubPluginVariantNotFoundError: If the plugin variant could not be found.
            HubConnectionError: If the Hub API could not be reached.
        """
        try:
            plugin = self.get_plugins_of_type(plugin_type, refresh=refresh)[plugin_name]
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

        cache_path = _index_cache_path(url)
        definition = None if refresh else _read_index_cache(cache_path)

        if definition is None:
            # A caller that accepts a cached definition is checking in the
            # background, so its fetch is not news to the reader.
            logger.log(
                logging.INFO if refresh else logging.DEBUG,
                "Fetching plugin definition from Meltano Hub",
                url=url,
            )
            response = self._get(url)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                reason = (
                    f"{response.reason or 'Unknown reason'} ({response.status_code}): "
                    "can not retrieve plugin"
                )
                raise HubConnectionError(reason)

            definition = response.json()
            _write_index_cache(cache_path, definition)

        return PluginDefinition(
            **definition,
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
        *,
        refresh: bool = True,
    ) -> dict[str, IndexedPlugin]:
        """Get all plugins of a given type.

        Args:
            plugin_type: The plugin type.
            refresh: Whether to fetch the index rather than reuse one cached
                in the last `INDEX_CACHE_DURATION`. Fetching is the default,
                because a caller that resolves a plugin must see one added to
                the Hub moments ago. Either way the index that is fetched is
                cached, for a caller that does opt out.

        Returns:
            The plugin definitions.

        Raises:
            HubPluginTypeNotFoundError: If the plugin type is not supported.
            HubConnectionError: If the Hub API could not be reached.
        """
        if not plugin_type.discoverable:
            return {}

        url = self.plugin_type_endpoint(plugin_type)
        cache_path = _index_cache_path(url)
        plugins: dict[str, dict[str, t.Any]] | None = (
            None if refresh else _read_index_cache(cache_path)
        )

        if plugins is None:
            response = self._get(url)

            if response.status_code == HTTPStatus.NOT_FOUND:
                raise HubPluginTypeNotFoundError(plugin_type)

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                reason = (
                    f"{response.reason or 'Unknown reason'} ({response.status_code}): "
                    f"can not retrieve plugins of type '{plugin_type.singular}'"
                )
                raise HubConnectionError(reason)

            plugins = response.json()
            _write_index_cache(cache_path, plugins)

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
