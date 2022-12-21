"""Discover plugin definitions."""

from __future__ import annotations

import io
import logging
import re
from abc import ABCMeta, abstractmethod
from typing import Iterable

import requests
from ruamel.yaml import YAMLError

import meltano
from meltano.core import bundle
from meltano.core.behavior.versioned import IncompatibleVersionError, Versioned
from meltano.core.discovery_file import DiscoveryFile
from meltano.core.plugin import BasePlugin, PluginDefinition, PluginRef, PluginType
from meltano.core.plugin.base import StandalonePlugin
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.factory import base_plugin_factory
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import NotFound, find_named
from meltano.core.yaml import yaml


class DiscoveryInvalidError(Exception):
    """Occurs when the discovery.yml fails to be parsed."""


class DiscoveryUnavailableError(Exception):
    """Occurs when the discovery.yml cannot be found or downloaded."""


# Increment this version number whenever the schema of discovery.yml is changed.
# See https://docs.meltano.com/contribute/plugins#discoveryyml-version for more information.
VERSION = 22


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
        ...  # noqa: WPS428

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


class PluginDiscoveryService(  # noqa: WPS214 (too many public methods)
    PluginRepository, Versioned
):
    """Discover plugin definitions."""

    __version__ = VERSION

    def __init__(self, project, discovery: dict | None = None):
        """Create a new PluginDiscoveryService.

        Args:
            project: The project to discover plugins for.
            discovery: The discovery file to use.
        """
        self.project = project

        self._discovery_version = None
        self._discovery = None
        if discovery:
            self._discovery_version = DiscoveryFile.file_version(discovery)
            self._discovery = DiscoveryFile.parse(discovery)

        self.settings_service = ProjectSettingsService(self.project)

    @property
    def file_version(self):
        """Return the version of the discovery file.

        Returns:
            The version of the discovery file.
        """
        return self._discovery_version

    @property
    def discovery_url(self):
        """Return the URL of the discovery file.

        Returns:
            The URL of the discovery file.
        """
        discovery_url = self.settings_service.get("discovery_url")

        if not discovery_url or not re.match(
            r"^https?://", discovery_url  # noqa: WPS360
        ):
            return None

        return discovery_url

    @property
    def discovery_url_auth(self):
        """Return the `discovery_url_auth` setting.

        Returns:
            The `discovery_url_auth` setting.
        """
        return self.settings_service.get("discovery_url_auth")

    @property
    def discovery(self):
        """Return first compatible discovery manifest from a few locations.

        Locations:

        - project local `discovery.yml`
        - `discovery_url` project setting
        - .meltano/cache/discovery.yml
        - meltano.core.bundle

        Returns:
            The discovery file.

        Raises:
            DiscoveryInvalidError: If the discovery file is invalid.
        """
        if self._discovery:
            return self._discovery

        loaders = [
            (
                self.load_local_discovery,
                "your project's local `discovery.yml` manifest",
            ),
            (
                self.load_remote_discovery,
                f"the `discovery.yml` manifest received from {self.discovery_url}",
            ),
            (self.load_cached_discovery, "the cached `discovery.yml` manifest"),
            (self.load_bundled_discovery, "the bundled `discovery.yml` manifest"),
        ]

        errored = False
        for loader, description in loaders:
            if errored:
                logging.warning(f"Falling back on {description}...")

            try:
                loader()
            except IncompatibleVersionError as err:
                errored = True

                logging.warning(
                    f"{description.capitalize()} has version {err.file_version}, while this version of Meltano requires version {err.version}."
                )
                if err.file_version > err.version:
                    logging.warning(
                        "Please install the latest compatible version of Meltano using `meltano upgrade`."
                    )
            except DiscoveryInvalidError as err:
                errored = True
                logging.error(f"{description.capitalize()} could not be parsed.")
                logging.debug(str(err))

            if self._discovery:
                return self._discovery

        raise DiscoveryInvalidError("No valid `discovery.yml` manifest could be found")

    def load_local_discovery(self):
        """Load the local `discovery.yml` manifest.

        Returns:
            The discovery file.
        """
        try:
            with self.project.root_dir("discovery.yml").open() as local_discovery:
                return self.load_discovery(local_discovery)
        except FileNotFoundError:
            pass

    def load_remote_discovery(self) -> DiscoveryFile | None:
        """Load the remote `discovery.yml` manifest.

        Returns:
            The discovery file.
        """
        discovery_url = self.discovery_url
        if not discovery_url:
            return None

        headers = {"User-Agent": f"Meltano/{meltano.__version__}"}  # noqa: WPS609
        params = {}

        if self.discovery_url_auth:
            headers["Authorization"] = self.discovery_url_auth

        if self.settings_service.get("send_anonymous_usage_stats"):
            project_id = self.settings_service.get("project_id")

            headers["X-Project-ID"] = project_id
            params["project_id"] = project_id

        try:
            response = requests.get(discovery_url, headers=headers, params=params)
            response.raise_for_status()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        ) as err:
            logging.debug("Remote `discovery.yml` manifest could not be downloaded.")
            logging.debug(str(err))
            return None

        remote_discovery = io.StringIO(response.text)

        return self.load_discovery(remote_discovery, cache=True)

    def load_cached_discovery(self):
        """Load the cached `discovery.yml` manifest.

        Returns:
            The discovery file.
        """
        try:
            with self.cached_discovery_file.open() as cached_discovery:
                return self.load_discovery(cached_discovery)
        except FileNotFoundError:
            pass

    def load_bundled_discovery(self):
        """Load the bundled `discovery.yml` manifest.

        Returns:
            The discovery file.
        """
        with open(bundle.root / "discovery.yml") as bundled_discovery:
            discovery = self.load_discovery(bundled_discovery, cache=True)

        return discovery

    def load_discovery(self, discovery_file, cache=False) -> DiscoveryFile:
        """Load the `discovery.yml` manifest.

        Args:
            discovery_file: The file to load.
            cache: Whether to cache the manifest.

        Returns:
            The discovery file.

        Raises:
            DiscoveryInvalidError: If the discovery file is invalid.
        """
        try:
            discovery_yaml = yaml.load(discovery_file)

            self._discovery_version = DiscoveryFile.file_version(discovery_yaml)
            self.ensure_compatible()

            self._discovery = DiscoveryFile.parse(discovery_yaml)

            if cache:
                self.cache_discovery()

            return self._discovery
        except (YAMLError, Exception) as err:
            raise DiscoveryInvalidError(str(err))

    def cache_discovery(self):
        """Cache the `discovery.yml` manifest."""
        with self.cached_discovery_file.open("w") as cached_discovery:
            yaml.dump(
                self._discovery,
                cached_discovery,
            )

    @property
    def cached_discovery_file(self):
        """Return the cached `discovery.yml` manifest file.

        Returns:
            The cached `discovery.yml` manifest file.
        """
        return self.project.meltano_dir("cache", "discovery.yml")

    def get_plugins_of_type(self, plugin_type):
        """Return the plugins of the given type.

        Args:
            plugin_type: The plugin type.

        Returns:
            The list of plugins of the given type.
        """
        return self.discovery[plugin_type]

    def plugins_by_type(self):
        """Return a mapping of plugins by type.

        Returns:
            The plugins by type.
        """
        return {
            plugin_type: self.get_plugins_of_type(plugin_type)
            for plugin_type in PluginType
        }

    def plugins(self) -> Iterable[PluginDefinition]:
        """Generate all plugins.

        Yields:
            Each discoverable plugin.
        """
        yield from (
            plugin
            for plugin_type, plugins in self.plugins_by_type().items()
            for plugin in plugins
        )

    def find_definition(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> PluginDefinition:
        """Find a plugin definition by type and name.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.

        Returns:
            The plugin definition.

        Raises:
            PluginNotFoundError: If the plugin could not be found.
        """
        try:
            return find_named(self.get_plugins_of_type(plugin_type), plugin_name)
        except NotFound as err:
            raise PluginNotFoundError(PluginRef(plugin_type, plugin_name)) from err

    def find_definition_by_namespace(
        self, plugin_type: PluginType, namespace: str
    ) -> PluginDefinition:
        """Find a plugin definition by type and namespace.

        Args:
            plugin_type: The plugin type.
            namespace: The plugin namespace.

        Returns:
            The plugin definition.

        Raises:
            PluginNotFoundError: If the plugin could not be found.
        """
        try:
            return next(
                plugin
                for plugin in self.get_plugins_of_type(plugin_type)
                if plugin.namespace == namespace
            )
        except StopIteration as stop:
            raise PluginNotFoundError(namespace) from stop

    def find_related_plugin_refs(
        self,
        target_plugin: ProjectPlugin,
        plugin_types: list[PluginType] | None = None,
    ):
        """Find related plugin references.

        Args:
            target_plugin: The target plugin.
            plugin_types: Types of related plugins to add.

        Returns:
            The related plugin references.
        """
        plugin_types = plugin_types or list(PluginType)

        try:
            plugin_types.remove(target_plugin.type)
        except ValueError:
            pass

        related_plugin_refs = []

        related_plugin_refs.extend(
            related_plugin_def
            for plugin_type in plugin_types
            for related_plugin_def in self.get_plugins_of_type(plugin_type)
            if related_plugin_def.namespace == target_plugin.namespace
        )

        return related_plugin_refs


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
