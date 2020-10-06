import os
import io
import yaml
import requests
import logging
import shutil
import re
from copy import deepcopy
from typing import Dict, Iterable, Optional

import meltano.core.bundle as bundle
from .project_settings_service import ProjectSettingsService
from .setting_definition import SettingDefinition
from .behavior.versioned import Versioned, IncompatibleVersionError
from .behavior.canonical import Canonical
from .config_service import ConfigService
from .plugin import PluginDefinition, ProjectPlugin, PluginType, PluginRef, Variant
from .plugin.factory import plugin_factory


class PluginNotFoundError(Exception):
    pass


class DiscoveryInvalidError(Exception):
    """Occurs when the discovery.yml fails to be parsed."""

    pass


class DiscoveryUnavailableError(Exception):
    """Occurs when the discovery.yml cannot be found or downloaded."""

    pass


# Increment this version number whenever the schema of discovery.yml is changed.
# See https://www.meltano.com/docs/contributor-guide.html#discovery-yml-version for more information.
VERSION = 16


class DiscoveryFile(Canonical):
    def __init__(self, version=1, **plugins):
        super().__init__(version=int(version))

        for plugin_type in PluginType:
            self[plugin_type] = []

        for plugin_type, raw_plugins in plugins.items():
            for raw_plugin in raw_plugins:
                plugin_def = PluginDefinition(
                    plugin_type,
                    raw_plugin.pop("name"),
                    raw_plugin.pop("namespace"),
                    **raw_plugin,
                )
                self[plugin_type].append(plugin_def)

    @classmethod
    def version(cls, attrs):
        return int(attrs.get("version", 1))


class PluginDiscoveryService(Versioned):
    __version__ = VERSION

    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        discovery: Optional[Dict] = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)

        self._discovery_version = None
        self._discovery = None
        if discovery:
            self._discovery_version = DiscoveryFile.version(discovery)
            self._discovery = DiscoveryFile.parse(discovery)

    @property
    def file_version(self):
        return self._discovery_version

    @property
    def discovery_url(self):
        discovery_url = ProjectSettingsService(self.project).get("discovery_url")

        if not discovery_url or not re.match(r"^https?://", discovery_url):
            return None

        return discovery_url

    @property
    def discovery(self):
        """
        Return first compatible discovery manifest from these locations:

        - project local `discovery.yml`
        - `discovery_url` project setting
        - .meltano/cache/discovery.yml
        - meltano.core.bundle
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
        try:
            with self.project.root_dir("discovery.yml").open() as local_discovery:
                return self.load_discovery(local_discovery)
        except FileNotFoundError:
            pass

    def load_remote_discovery(self):
        if not self.discovery_url:
            return

        try:
            response = requests.get(self.discovery_url)
            response.raise_for_status()

            remote_discovery = io.StringIO(response.text)
            discovery = self.load_discovery(remote_discovery, cache=True)

            return discovery
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        ) as err:
            logging.debug("Remote `discovery.yml` manifest could not be downloaded.")
            logging.debug(str(err))
            pass

    def load_cached_discovery(self):
        try:
            with self.cached_discovery_file.open() as cached_discovery:
                return self.load_discovery(cached_discovery)
        except FileNotFoundError:
            pass

    def load_bundled_discovery(self):
        with bundle.find("discovery.yml").open() as bundled_discovery:
            discovery = self.load_discovery(bundled_discovery, cache=True)

        return discovery

    def load_discovery(self, discovery_file, cache=False):
        try:
            discovery_yaml = yaml.safe_load(discovery_file)

            self._discovery_version = DiscoveryFile.version(discovery_yaml)
            self.ensure_compatible()

            self._discovery = DiscoveryFile.parse(discovery_yaml)

            if cache:
                self.cache_discovery()

            return self._discovery
        except IncompatibleVersionError:
            raise
        except (yaml.YAMLError, Exception) as err:
            raise DiscoveryInvalidError(str(err))

    def cache_discovery(self):
        with self.cached_discovery_file.open("w") as cached_discovery:
            yaml.dump(
                self._discovery,
                cached_discovery,
                default_flow_style=False,
                sort_keys=False,
            )

    @property
    def cached_discovery_file(self):
        return self.project.meltano_dir("cache", "discovery.yml")

    def get_discovery_plugins_of_type(self, plugin_type):
        return self.discovery[plugin_type]

    def get_custom_plugins_of_type(self, plugin_type):
        return [
            project_plugin.custom_definition
            for project_plugin in self.config_service.get_plugins_of_type(plugin_type)
            if project_plugin.is_custom()
        ]

    def get_plugins_of_type(self, plugin_type):
        return self.get_custom_plugins_of_type(
            plugin_type
        ) + self.get_discovery_plugins_of_type(plugin_type)

    def plugins_by_type(self):
        return {
            plugin_type: self.get_plugins_of_type(plugin_type)
            for plugin_type in PluginType
        }

    def plugins(self) -> Iterable[PluginDefinition]:
        yield from (
            plugin
            for plugin_type, plugins in self.plugins_by_type().items()
            for plugin in plugins
        )

    def find_definition(
        self, plugin_type: PluginType, plugin_name: str, variant=None
    ) -> PluginDefinition:
        name, _ = PluginRef.parse_name(plugin_name)
        try:
            plugin = next(
                plugin
                for plugin in self.get_plugins_of_type(plugin_type)
                if plugin.name == name
            )
            plugin.use_variant(variant)
            return plugin
        except StopIteration as stop:
            raise PluginNotFoundError(name) from stop

    def find_definition_by_namespace(
        self, plugin_type: PluginType, namespace: str
    ) -> PluginDefinition:
        try:
            return next(
                plugin
                for plugin in self.get_plugins_of_type(plugin_type)
                if plugin.namespace == namespace
            )
        except StopIteration as stop:
            raise PluginNotFoundError(namespace) from stop

    def get_definition(self, project_plugin: ProjectPlugin) -> PluginDefinition:
        if project_plugin.is_custom():
            plugin = project_plugin.custom_definition
        else:
            try:
                plugin = next(
                    plugin for plugin in self.plugins() if plugin == project_plugin
                )
            except StopIteration as stop:
                raise PluginNotFoundError(project_plugin.name) from stop

        plugin.use_variant(project_plugin.variant or Variant.ORIGINAL_NAME)

        return plugin
