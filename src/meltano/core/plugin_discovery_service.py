import os
import io
import yaml
import requests
import logging
import shutil
import re
from copy import deepcopy
from typing import Dict, Iterator, Optional
from itertools import groupby, chain

import meltano.core.bundle as bundle
from .project_settings_service import ProjectSettingsService
from .setting_definition import SettingDefinition
from .behavior.versioned import Versioned, IncompatibleVersionError
from .behavior.canonical import Canonical
from .config_service import ConfigService
from .plugin import Plugin, PluginInstall, PluginType, PluginRef
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
VERSION = 13


class DiscoveryFile(Canonical):
    def __init__(self, version=1, **plugins):
        super().__init__(version=int(version))

        for plugin_type in PluginType:
            self[plugin_type] = []

        for plugin_type, plugin_defs in plugins.items():
            for plugin_def in plugin_defs:
                plugin = Plugin(
                    plugin_type,
                    plugin_def.pop("name"),
                    plugin_def.pop("namespace"),
                    **plugin_def,
                )
                self[plugin_type].append(plugin)

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

    def plugins(self) -> Iterator[Plugin]:
        discovery_plugins = (
            plugin
            for plugin_type in PluginType
            for plugin in self.discovery[plugin_type]
        )

        yield from self.custom_plugins()
        yield from discovery_plugins

    def custom_plugins(self) -> Iterator[Plugin]:
        # some plugins in the Meltano file might be custom, thus they
        # serve both as `PluginInstall` and `Plugin`
        custom_plugin_type_defs = (
            (custom_plugin.type, custom_plugin.canonical())
            for custom_plugin in self.config_service.plugins()
            if custom_plugin.is_custom()
        )

        custom_plugins = (
            Plugin(
                plugin_type,
                custom_plugin_def.pop("name"),
                custom_plugin_def.pop("namespace"),
                **custom_plugin_def,
            )
            for plugin_type, custom_plugin_def in custom_plugin_type_defs
        )

        yield from custom_plugins

    def find_plugin(self, plugin_type: PluginType, plugin_name: str):
        name, _ = PluginRef.parse_name(plugin_name)
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if (plugin.type == plugin_type and plugin.name == name)
            )
        except StopIteration:
            raise PluginNotFoundError(name)

    def find_plugin_by_namespace(self, plugin_type: PluginType, namespace: str):
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if (plugin.type == plugin_type and plugin.namespace == namespace)
            )
        except StopIteration as stop:
            raise PluginNotFoundError(namespace) from stop

    def discover(self, plugin_type: PluginType = None):
        """Return a pretty printed list of available plugins."""
        enabled_plugin_types = [plugin_type] if plugin_type else list(PluginType)

        return {
            plugin_type: [p.name for p in plugins]
            for plugin_type, plugins in groupby(self.plugins(), lambda p: p.type)
            if plugin_type in enabled_plugin_types
        }

    def list_discovery(self, discovery):
        return "\n".join(
            plugin.name for plugin in self.plugins() if plugin.type == discovery
        )
