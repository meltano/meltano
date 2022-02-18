import io
import logging
import re
from typing import Dict, Iterable, List, Optional

import requests
import yaml

import meltano
import meltano.core.bundle as bundle

from .behavior.canonical import Canonical
from .behavior.versioned import IncompatibleVersionError, Versioned
from .plugin import BasePlugin, PluginDefinition, PluginRef, PluginType
from .plugin.error import PluginNotFoundError
from .plugin.factory import base_plugin_factory
from .plugin.project_plugin import ProjectPlugin
from .project_settings_service import ProjectSettingsService
from .utils import NotFound, find_named


class DiscoveryInvalidError(Exception):
    """Occurs when the discovery.yml fails to be parsed."""


class DiscoveryUnavailableError(Exception):
    """Occurs when the discovery.yml cannot be found or downloaded."""


# Increment this version number whenever the schema of discovery.yml is changed.
# See https://www.meltano.com/docs/contributor-guide.html#discovery-yml-version for more information.
VERSION = 20


class DiscoveryFile(Canonical):
    def __init__(self, version=1, **plugins):
        super().__init__(version=int(version))

        for ptype in PluginType:
            self[ptype] = []

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
    def file_version(cls, attrs):
        """Return version of discovery file represented by attrs dictionary."""
        return int(attrs.get("version", 1))


class PluginDiscoveryService(Versioned):
    __version__ = VERSION

    def __init__(self, project, discovery: Optional[Dict] = None):
        self.project = project

        self._discovery_version = None
        self._discovery = None
        if discovery:
            self._discovery_version = DiscoveryFile.file_version(discovery)
            self._discovery = DiscoveryFile.parse(discovery)

        self.settings_service = ProjectSettingsService(self.project)

    @property
    def file_version(self):
        return self._discovery_version

    @property
    def discovery_url(self):
        discovery_url = self.settings_service.get("discovery_url")

        if not discovery_url or not re.match(r"^https?://", discovery_url):
            return None

        return discovery_url

    @property
    def discovery_url_auth(self):
        """Return the `discovery_url_auth` setting."""
        return self.settings_service.get("discovery_url_auth")

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
        discovery_url = self.discovery_url
        if not discovery_url:
            return

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
            return

        remote_discovery = io.StringIO(response.text)
        discovery = self.load_discovery(remote_discovery, cache=True)

        return discovery

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

            self._discovery_version = DiscoveryFile.file_version(discovery_yaml)
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

    def get_plugins_of_type(self, plugin_type):
        return self.discovery[plugin_type]

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
        self, plugin_type: PluginType, plugin_name: str
    ) -> PluginDefinition:
        try:
            return find_named(self.get_plugins_of_type(plugin_type), plugin_name)
        except NotFound as err:
            raise PluginNotFoundError(PluginRef(plugin_type, plugin_name)) from err

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

    def find_base_plugin(
        self, plugin_type: PluginType, plugin_name: str, variant=None
    ) -> BasePlugin:
        plugin = self.find_definition(plugin_type, plugin_name)
        return base_plugin_factory(plugin, variant)

    def get_base_plugin(self, project_plugin: ProjectPlugin) -> BasePlugin:
        plugin = project_plugin.custom_definition or self.find_definition(
            project_plugin.type, project_plugin.inherit_from or project_plugin.name
        )

        return base_plugin_factory(plugin, project_plugin.variant)

    def find_related_plugin_refs(
        self,
        target_plugin: ProjectPlugin,
        plugin_types: List[PluginType] = list(PluginType),
    ):
        try:
            plugin_types.remove(target_plugin.type)
        except ValueError:
            pass

        related_plugin_refs = []

        runner_ref = target_plugin.runner
        if runner_ref:
            related_plugin_refs.append(runner_ref)

        related_plugin_refs.extend(
            related_plugin_def
            for plugin_type in plugin_types
            for related_plugin_def in self.get_plugins_of_type(plugin_type)
            if related_plugin_def.namespace == target_plugin.namespace
        )

        return related_plugin_refs
