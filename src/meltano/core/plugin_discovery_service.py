import os
import yaml
import requests
import logging
from typing import Dict, List, Optional
from itertools import groupby

import meltano.core.bundle as bundle
from .plugin import Plugin, PluginType
from .plugin.factory import plugin_factory
from .behavior.versioned import Versioned, IncompatibleVersionError


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
    __version__ = 1

    def __init__(self, project, discovery: Optional[Dict] = None):
        self.project = project
        self._discovery = discovery

    @property
    def backend_version(self):
        return int(self._discovery.get("version", 1))

    @property
    def discovery(self):
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
        except IncompatibleVersionError:
            # let's default to the local cache
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
        except yaml.YAMLError:
            logging.debug(
                f"Discovery cache corrupted, deleting {self.cached_discovery_file}"
            )
            self.cached_discovery_file.unlink()
            return {}

    @property
    def cached_discovery_file(self):
        return self.project.meltano_dir("cache", "discovery.yml")

    def plugins(self) -> List[Plugin]:
        """Parse the discovery file and returns it as `Plugin` instances."""
        # this will parse the discovery file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        plugins = self.discovery.copy()
        plugins.pop("version", 1)

        return (
            plugin_factory(plugin_type, plugin_def)
            for plugin_type, plugin_defs in plugins.items()
            for plugin_def in sorted(plugin_defs, key=lambda k: k["name"])
            if PluginType.value_exists(plugin_type)
        )

    def find_plugin(self, plugin_type: PluginType, plugin_name: str):
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if (plugin.type == plugin_type and plugin.name == plugin_name)
            )
        except StopIteration:
            raise PluginNotFoundError()

    def discover(self, plugin_type: PluginType):
        """Return a pretty printed list of available plugins."""
        enabled_plugin_types = (
            (
                PluginType.EXTRACTORS,
                PluginType.LOADERS,
                PluginType.TRANSFORMERS,
                PluginType.MODELS,
                PluginType.TRANSFORMS,
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
