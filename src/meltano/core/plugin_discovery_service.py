import os
import yaml
import requests
import logging
import shutil
from copy import deepcopy
from typing import Dict, Iterator, Optional
from itertools import groupby, chain

import meltano.core.bundle as bundle
from .behavior.versioned import Versioned, IncompatibleVersionError
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


class PluginDiscoveryService(Versioned):
    __version__ = 3

    def __init__(
        self,
        project,
        config_service: ConfigService = None,
        discovery: Optional[Dict] = None,
    ):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self._discovery = discovery

    @property
    def backend_version(self):
        return int(self._discovery.get("version", 1))

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
                    self._discovery = yaml.load(local) or {}
            else:
                return self.fetch_discovery()

            self.ensure_compatible()

            return self._discovery
        except (yaml.YAMLError, FileNotFoundError) as e:
            raise DiscoveryInvalidError("discovery.yml is not well formed.") from e
        except IncompatibleVersionError as e:
            logging.fatal(
                "This version of Meltano cannot parse the plugins manifest, please update Meltano."
            )
            self._discovery = None
            raise

    def fetch_discovery(self):
        try:
            response = requests.get(MELTANO_DISCOVERY_URL)
            response.raise_for_status()
            self._discovery = yaml.load(response.text)
            self.ensure_compatible()

            with self.cached_discovery_file.open("w") as discovery_cache:
                discovery_cache.write(response.text)
            logging.debug(f"Discovery cache updated at {self.cached_discovery_file}")
        except (requests.exceptions.HTTPError, yaml.YAMLError) as e:
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
    def cached_discovery(self):
        try:
            with self.cached_discovery_file.open() as discovery_cache:
                return yaml.load(discovery_cache)
        except (yaml.YAMLError, FileNotFoundError):
            logging.debug(
                f"Discovery cache corrupted or missing, falling back on the bundled discovery."
            )
            shutil.copy(bundle.find("discovery.yml"), self.cached_discovery_file)

            # load it back
            with self.cached_discovery_file.open() as discovery_cache:
                return yaml.load(discovery_cache)

    @property
    def cached_discovery_file(self):
        return self.project.meltano_dir("cache", "discovery.yml")

    def plugins(self) -> Iterator[Plugin]:
        custom_plugins = self.make_plugins(self.project.meltano.get("plugins", {}))
        discovery_plugins = self.make_plugins(self.discovery)

        return chain(custom_plugins, discovery_plugins)

    def make_plugins(self, plugin_defs: Dict) -> Iterator[Plugin]:
        plugins = deepcopy(plugin_defs)
        plugins.pop("version", 1)

        return (
            Plugin(
                plugin_type,
                plugin_def.pop("name"),
                plugin_def.pop("namespace"),
                **plugin_def,
            )
            for plugin_type, plugin_defs in plugins.items()
            for plugin_def in sorted(plugin_defs, key=lambda d: d["name"])
            if (PluginType.value_exists(plugin_type) and "namespace" in plugin_def)
        )

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

    def discover(self, plugin_type: PluginType):
        """Return a pretty printed list of available plugins."""
        enabled_plugin_types = (
            (
                PluginType.EXTRACTORS,
                PluginType.LOADERS,
                PluginType.TRANSFORMERS,
                PluginType.MODELS,
                PluginType.TRANSFORMS,
                PluginType.CONNECTIONS,
                PluginType.ORCHESTRATORS,
            )
            if plugin_type == PluginType.ALL
            else (plugin_type,)
        )
        return {
            plugin_type: [p.name for p in plugins]
            for plugin_type, plugins in groupby(self.plugins(), lambda p: p.type)
            if plugin_type in enabled_plugin_types
        }

    def list_discovery(self, discovery):
        return "\n".join(
            plugin.name for plugin in self.plugins() if plugin.type == discovery
        )
