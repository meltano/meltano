import os
import io
import yaml
import requests
import logging
import shutil
from copy import deepcopy
from typing import Dict, Iterator, Optional
from itertools import groupby, chain

import meltano.core.bundle as bundle
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


MELTANO_DISCOVERY_URL = "https://www.meltano.com/discovery.yml"

# Increment this version number whenever the schema of discovery.yml is changed.
# See https://www.meltano.com/developer-tools/contributor-guide.html#discovery-yml-version for more information.
VERSION = 10


class DiscoveryFile(Canonical):
    def __init__(self, **attrs):
        version = int(attrs.pop("version", 1))

        super().__init__(version=version)

        for plugin_type, plugin_defs in attrs.items():
            self[plugin_type] = []

            for plugin_def in plugin_defs:
                plugin = Plugin(
                    plugin_type,
                    plugin_def.pop("name"),
                    plugin_def.pop("namespace"),
                    **plugin_def,
                )
                self[plugin_type].append(plugin)


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
        self._discovery = DiscoveryFile.parse(discovery)

    @property
    def backend_version(self):
        return int(self._discovery.version)

    @property
    def discovery(self):
        """
        Return first compatible discovery manifest from these locations:

        - project local `discovery.yml`
        - http://meltano.com/discovery.yml
        - .meltano/cache/discovery.yml
        - meltano.core.bundle
        """
        if self._discovery:
            return self._discovery

        try:
            local_discovery = self.project.root.joinpath("discovery.yml")

            if local_discovery.is_file():
                with local_discovery.open() as local:
                    self._discovery = self.load_discovery(local)
            else:
                self._discovery = self.fetch_discovery()
        except DiscoveryInvalidError as e:
            # let's use the bundled one
            logging.error(
                "Meltano could not parse the `discovery.yml` returned by the server."
            )
            logging.debug(str(e))
            self._discovery = self.cached_discovery

        try:
            self.ensure_compatible()
        except IncompatibleVersionError as e:
            logging.fatal(
                "This version of Meltano cannot parse the plugins manifest, please update Meltano."
            )
            self._discovery = None
            raise

        return self._discovery

    def fetch_discovery(self):
        try:
            response = requests.get(MELTANO_DISCOVERY_URL)
            response.raise_for_status()
            self._discovery = self.load_discovery(io.StringIO(response.text))
            self.ensure_compatible()

            with self.cached_discovery_file.open("w") as discovery_cache:
                discovery_cache.write(response.text)
            logging.debug(f"Discovery cache updated at {self.cached_discovery_file}")
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            yaml.YAMLError,
        ) as e:
            # let's try loading the cache instead
            self._discovery = self.cached_discovery
        except IncompatibleVersionError as e:
            # let's default to the local cache
            if e.backend_version > e.version:
                logging.warning("You must update Meltano to get new plugins updates.")
            self._discovery = self.cached_discovery

        if not self._discovery:
            raise DiscoveryInvalidError("Cannot parse discovery.yml.")

        return self._discovery

    @property
    def cached_discovery(self) -> DiscoveryFile:
        try:
            with self.cached_discovery_file.open() as discovery_cache:
                return self.load_discovery(discovery_cache)
        except (yaml.YAMLError, FileNotFoundError, DiscoveryInvalidError):
            logging.debug(
                f"Discovery cache corrupted or missing, falling back on the bundled discovery."
            )
            shutil.copy(bundle.find("discovery.yml"), self.cached_discovery_file)

            # load it back
            with self.cached_discovery_file.open() as discovery_cache:
                return self.load_discovery(discovery_cache)

    @property
    def cached_discovery_file(self):
        return self.project.meltano_dir("cache", "discovery.yml")

    def load_discovery(self, discovery_file) -> DiscoveryFile:
        try:
            return DiscoveryFile.parse(yaml.safe_load(discovery_file))
        except Exception as err:
            raise DiscoveryInvalidError(str(err))

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

    def discover(self, plugin_type: PluginType = None):
        """Return a pretty printed list of available plugins."""
        enabled_plugin_types = (plugin_type,) if plugin_type else iter(PluginType)

        return {
            plugin_type: [p.name for p in plugins]
            for plugin_type, plugins in groupby(self.plugins(), lambda p: p.type)
            if plugin_type in enabled_plugin_types
        }

    def list_discovery(self, discovery):
        return "\n".join(
            plugin.name for plugin in self.plugins() if plugin.type == discovery
        )
