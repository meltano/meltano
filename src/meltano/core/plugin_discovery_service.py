import os
import yaml
import requests
import logging
from copy import deepcopy
from typing import Dict, Iterator, Optional
from itertools import groupby, chain

import meltano.core.bundle as bundle
from .plugin import Plugin, PluginInstall, PluginType
from .plugin.factory import plugin_factory
from .behavior.versioned import Versioned, IncompatibleVersionError
from .config_service import ConfigService


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
    __version__ = 2

    def __init__(self, project,
                 config_service: ConfigService = None,
                 discovery: Optional[Dict] = None):
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

    def plugins(self) -> Iterator[Plugin]:
        return chain(self.custom_plugins(), self.discovery_plugins())

    def discovery_plugins(self) -> Iterator[Plugin]:
        """Parse the discovery file and returns it as `Plugin` instances."""

        # this will parse the discovery file and create an instance of the
        # corresponding `plugin_class` for all the plugins.
        plugins = deepcopy(self.discovery)
        plugins.pop("version", 1)

        return (
            Plugin(plugin_type,
                   plugin_def.pop('name'),
                   plugin_def.pop('namespace'),
                   plugin_def.pop('pip_url'),
                   **plugin_def)
            for plugin_type, plugin_defs in plugins.items()
            for plugin_def in plugin_defs
        )

    def custom_plugins(self) -> Iterator[Plugin]:
        """Parse the meltano.yml and return all defined `Plugin`."""

        plugins = deepcopy(self.project.meltano.get('plugins', {}))

        return (
            Plugin(plugin_type,
                   plugin_def.pop('name'),
                   plugin_def.pop('namespace'),
                   plugin_def.pop('pip_url'),
                   **plugin_def)
            for plugin_type, plugin_defs in plugins.items()
            for plugin_def in plugin_defs
            if 'namespace' in plugin_def
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
