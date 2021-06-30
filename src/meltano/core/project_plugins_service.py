import logging
import os
from contextlib import contextmanager
from typing import Iterable, List, Optional

import yaml
from meltano.core.utils import NotFound, find_named

from .config_service import ConfigService
from .plugin import PluginRef, PluginType
from .plugin.error import PluginNotFoundError, PluginParentNotFoundError
from .plugin.project_plugin import ProjectPlugin
from .plugin_discovery_service import PluginDiscoveryService
from .project import Project

logger = logging.getLogger(__name__)


class PluginAlreadyAddedException(Exception):
    def __init__(self, plugin: PluginRef):
        self.plugin = plugin
        super().__init__()


class ProjectPluginsService:
    def __init__(
        self,
        project: Project,
        config_service: ConfigService = None,
        discovery_service: PluginDiscoveryService = None,
        use_cache=True,
    ):
        self.project = project

        self.config_service = config_service or ConfigService(project)
        self.discovery_service = discovery_service or PluginDiscoveryService(project)

        self._current_plugins = None
        self._use_cache = use_cache

    @property
    def current_plugins(self):
        if self._current_plugins is None or not self._use_cache:
            self._current_plugins = self.config_service.current_meltano_yml.plugins
        return self._current_plugins

    @contextmanager
    def update_plugins(self):
        with self.config_service.update_meltano_yml() as meltano_yml:
            yield meltano_yml.plugins

        self._current_plugins = None

    def add_to_file(self, plugin: ProjectPlugin):
        if not plugin.should_add_to_file():
            return plugin

        try:
            existing_plugin = self.get_plugin(plugin)
            raise PluginAlreadyAddedException(existing_plugin)
        except PluginNotFoundError:
            pass

        with self.update_plugins() as plugins:
            if not plugin.type in plugins:
                plugins[plugin.type] = []

            plugins[plugin.type].append(plugin)

        return plugin

    def remove_from_file(self, plugin: ProjectPlugin):
        """Remove plugin from `meltano.yml`."""
        # Will raise if the plugin isn't actually in the file
        self.get_plugin(plugin)

        with self.update_plugins() as plugins:
            plugins[plugin.type].remove(plugin)

        return plugin

    def has_plugin(self, plugin_name: str):
        try:
            self.find_plugin(plugin_name)
            return True
        except PluginNotFoundError:
            return False

    def find_plugin(
        self,
        plugin_name: str,
        plugin_type: Optional[PluginType] = None,
        invokable=None,
        configurable=None,
    ) -> ProjectPlugin:
        if "@" in plugin_name:
            plugin_name, profile_name = plugin_name.split("@", 2)
            logger.warning(
                f"Plugin configuration profiles are no longer supported, ignoring `@{profile_name}` in plugin name."
            )

        try:
            plugin = next(
                plugin
                for plugin in self.plugins(ensure_parent=False)
                if (
                    plugin.name == plugin_name
                    and (plugin_type is None or plugin.type == plugin_type)
                    and (
                        invokable is None
                        or self.ensure_parent(plugin).is_invokable() == invokable
                    )
                    and (
                        configurable is None
                        or self.ensure_parent(plugin).is_configurable() == configurable
                    )
                )
            )

            return self.ensure_parent(plugin)
        except StopIteration as stop:
            raise PluginNotFoundError(
                PluginRef(plugin_type, plugin_name) if plugin_type else plugin_name
            ) from stop

    def find_plugin_by_namespace(
        self, plugin_type: PluginType, namespace: str
    ) -> ProjectPlugin:
        """
        Find a plugin based on its PluginType and namespace.

        For example, PluginType.EXTRACTORS and namespace tap_custom
        will return the extractor for the tap-custom plugin.
        """
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if plugin.namespace == namespace and plugin_type == plugin.type
            )
        except StopIteration as stop:
            raise PluginNotFoundError(namespace) from stop

    def get_plugin(self, plugin_ref: PluginRef) -> ProjectPlugin:
        try:
            plugin = next(
                plugin
                for plugin in self.plugins(ensure_parent=False)
                if plugin == plugin_ref
            )

            return self.ensure_parent(plugin)
        except StopIteration as stop:
            raise PluginNotFoundError(plugin_ref) from stop

    def get_plugins_of_type(self, plugin_type, ensure_parent=True):
        """Return plugins of specified type."""
        plugins = self.current_plugins[plugin_type]

        if ensure_parent:
            for plugin in plugins:
                self.ensure_parent(plugin)

        return plugins

    def plugins_by_type(self, ensure_parent=True):
        """Return plugins grouped by type."""
        return {
            plugin_type: self.get_plugins_of_type(
                plugin_type, ensure_parent=ensure_parent
            )
            for plugin_type in PluginType
        }

    def plugins(self, ensure_parent=True) -> Iterable[ProjectPlugin]:
        """Return all plugins."""
        yield from (
            plugin
            for _, plugins in self.plugins_by_type(ensure_parent=ensure_parent).items()
            for plugin in plugins
        )

    def update_plugin(self, plugin: ProjectPlugin):
        with self.update_plugins() as plugins:
            # find the proper plugin to update
            idx, outdated = next(
                (i, it) for i, it in enumerate(plugins[plugin.type]) if it == plugin
            )

            plugins[plugin.type][idx] = plugin

            return outdated

    def get_parent(self, plugin: ProjectPlugin):
        """Get plugin's parent plugin."""
        if plugin.inherit_from and not plugin.is_variant_set:
            try:
                return self.find_plugin(
                    plugin_type=plugin.type, plugin_name=plugin.inherit_from
                )
            except PluginNotFoundError:
                pass

        try:
            return self.discovery_service.get_base_plugin(plugin)
        except PluginNotFoundError as err:
            if plugin.inherit_from:
                raise PluginParentNotFoundError(plugin, err) from err

            raise

    def ensure_parent(self, plugin: ProjectPlugin):
        """Ensure that plugin has a parent set."""
        if not plugin.parent:
            plugin.parent = self.get_parent(plugin)

        return plugin
