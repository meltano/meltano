import logging
import os
from contextlib import contextmanager
from typing import Iterable, List, Optional

import yaml
from meltano.core.utils import NotFound, find_named

from .config_service import ConfigService
from .plugin import PluginRef, PluginType, Variant
from .plugin.error import PluginMissingError
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
            plugins = self.config_service.current_meltano_yml.plugins

            for plugin_type, plugins_of_type in plugins:
                for plugin in plugins_of_type:
                    plugin.parent = self.discovery_service.get_base_plugin(plugin)

            self._current_plugins = plugins
        return self._current_plugins

    @contextmanager
    def update_plugins(self):
        with self.config_service.update_meltano_yml() as meltano_yml:
            yield meltano_yml.plugins

        self._current_plugins = None

    def add_to_file(self, plugin: ProjectPlugin):
        if not plugin.should_add_to_file():
            return plugin

        if plugin in self.plugins():
            raise PluginAlreadyAddedException(plugin)

        with self.update_plugins() as plugins:
            if not plugin.type in plugins:
                plugins[plugin.type] = []

            plugins[plugin.type].append(plugin)

        return plugin

    def has_plugin(self, plugin_name: str):
        try:
            self.find_plugin(plugin_name)
            return True
        except PluginMissingError:
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
                for plugin in self.plugins()
                if (
                    plugin.name == plugin_name
                    and (plugin_type is None or plugin.type == plugin_type)
                    and (invokable is None or plugin.is_invokable() == invokable)
                    and (
                        configurable is None or plugin.is_configurable() == configurable
                    )
                )
            )

            return plugin
        except StopIteration as stop:
            raise PluginMissingError(plugin_name) from stop

    def get_plugin(self, plugin_ref: PluginRef) -> ProjectPlugin:
        try:
            plugin = next(plugin for plugin in self.plugins() if plugin == plugin_ref)

            return plugin
        except StopIteration as stop:
            raise PluginMissingError(plugin_ref.name) from stop

    def get_plugins_of_type(self, plugin_type):
        return self.current_plugins[plugin_type]

    def plugins_by_type(self):
        return {
            plugin_type: self.get_plugins_of_type(plugin_type)
            for plugin_type in PluginType
        }

    def plugins(self) -> Iterable[ProjectPlugin]:
        yield from (
            plugin
            for plugin_type, plugins in self.plugins_by_type().items()
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
