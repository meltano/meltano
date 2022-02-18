"""Project Plugin Service."""

from contextlib import contextmanager
from typing import Generator, List, Optional

import structlog

from meltano.core.environment import Environment, EnvironmentPluginConfig

from .config_service import ConfigService
from .plugin import PluginRef, PluginType
from .plugin.error import PluginNotFoundError, PluginParentNotFoundError
from .plugin.project_plugin import ProjectPlugin
from .plugin_discovery_service import PluginDiscoveryService
from .project import Project

logger = structlog.stdlib.get_logger(__name__)


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

    @contextmanager
    def update_environments(self):
        """Update Meltano environments in `meltano.yml`.

        Yields:
            The updated environments.
        """
        with self.config_service.update_meltano_yml() as meltano_yml:
            yield meltano_yml.environments

    def add_to_file(self, plugin: ProjectPlugin):
        if not plugin.should_add_to_file():
            return plugin

        try:
            existing_plugin = self.get_plugin(plugin)
            raise PluginAlreadyAddedException(existing_plugin)
        except PluginNotFoundError:
            pass

        with self.update_plugins() as plugins:
            if plugin.type not in plugins:
                plugins[plugin.type] = []

            plugins[plugin.type].append(plugin)

        return plugin

    def remove_from_file(self, plugin: ProjectPlugin):
        """Remove plugin from `meltano.yml`.

        Args:
            plugin: The plugin to remove.

        Returns:
            The removed plugin.
        """
        # Will raise if the plugin isn't actually in the file
        self.get_plugin(plugin)

        with self.update_plugins() as plugins:
            plugins[plugin.type].remove(plugin)

        return plugin

    def has_plugin(self, plugin_name: str) -> bool:
        """Check if plugin exists for the given name.

        Args:
            plugin_name: The name of the plugin to check for.

        Returns:
            True if the plugin exists, False otherwise.
        """
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
        """
        Find a plugin.

        Args:
            plugin_name: The name of the plugin to find.
            plugin_type: Optionally the type of plugin.
            invokable: Optionally limit the search to invokable plugins.
            configurable: Optionally limit the search to configurable plugins.

        Returns:
            The plugin.

        Raises:
            PluginNotFoundError: If the plugin is not found.
        """
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

        Args:
            plugin_type: The type of plugin to find.
            namespace: The namespace of the plugin.

        Returns:
            The plugin if found.

        Raises:
            PluginNotFoundError: If no plugin is found.
        """
        try:
            return next(
                plugin
                for plugin in self.plugins()
                if plugin.namespace == namespace and plugin_type == plugin.type
            )
        except StopIteration as stop:
            raise PluginNotFoundError(namespace) from stop

    def find_plugins_by_mapping_name(self, mapping_name: str) -> List[ProjectPlugin]:
        """Search for plugins with the specified mapping name present in  their mappings config.

        Args:
            mapping_name: The name of the mapping to find.

        Returns:
            The mapping plugins with the specified mapping name.

        Raises:
            PluginNotFoundError: If no mapper plugin with the specified mapping name is found.
        """
        found: List[ProjectPlugin] = []
        for plugin in self.get_plugins_of_type(plugin_type=PluginType.MAPPERS):
            if plugin.extra_config.get("_mapping_name") == mapping_name:
                found.append(plugin)
        if not found:
            raise PluginNotFoundError(mapping_name)
        return found

    def get_plugin(self, plugin_ref: PluginRef) -> ProjectPlugin:
        """Get a plugin using its PluginRef.

        Args:
            plugin_ref: The plugin reference to use.

        Returns:
            The plugin if found.

        Raises:
            PluginNotFoundError: If the plugin is not found.
        """
        try:
            plugin = next(
                plugin
                for plugin in self.plugins(ensure_parent=False)
                if plugin == plugin_ref
            )

            return self.ensure_parent(plugin)
        except StopIteration as stop:
            raise PluginNotFoundError(plugin_ref) from stop

    def get_plugins_of_type(
        self, plugin_type: PluginType, ensure_parent=True
    ) -> List[ProjectPlugin]:
        """Return plugins of specified type.

        Args:
            plugin_type: The type of the plugins to return.
            ensure_parent: If True, ensure that plugin has a parent plugin set.

        Returns:
            A list of plugins of the specified plugin type.
        """
        plugins = self.current_plugins[plugin_type]

        if ensure_parent:
            for plugin in plugins:
                self.ensure_parent(plugin)

        return plugins

    def plugins_by_type(self, ensure_parent=True):
        """Return plugins grouped by type.

        Args:
            ensure_parent: If True, ensure that plugin has a parent plugin set.

        Returns:
            A dict of plugins grouped by type.
        """
        return {
            plugin_type: self.get_plugins_of_type(
                plugin_type, ensure_parent=ensure_parent
            )
            for plugin_type in PluginType
        }

    def plugins(self, ensure_parent=True) -> Generator[ProjectPlugin, None, None]:
        """Return all plugins.

        Args:
            ensure_parent: If True, ensure that plugin has a parent plugin set.

        Yields:
            A generator of all plugins.
        """
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

    def update_environment_plugin(self, plugin: EnvironmentPluginConfig) -> None:
        """Update a plugin configuration inside a Meltano environment.

        Args:
            plugin: The plugin configuration to update.

        Returns:
            None
        """
        environments: List[Environment]
        environment = self.project.active_environment

        with self.update_environments() as environments:
            # find the proper environment to update
            env_idx, _ = next(
                (idx, env) for idx, env in enumerate(environments) if env == environment
            )

            # find the proper plugin to update
            environment.config.plugins.setdefault(plugin.type, [])
            p_idx, p_outdated = next(
                (
                    (idx, plg)
                    for idx, plg in enumerate(environment.config.plugins[plugin.type])
                    if plg == plugin
                ),
                (None, None),
            )

            active_environment = environments[env_idx]

            if p_idx is None:
                active_environment.config.plugins.setdefault(plugin.type, [])
                active_environment.config.plugins[plugin.type].append(plugin)
            else:
                active_environment.config.plugins[plugin.type][p_idx] = plugin

            return p_outdated

    def get_parent(self, plugin: ProjectPlugin) -> Optional[ProjectPlugin]:
        """Get plugin's parent plugin.

        Args:
            plugin: The plugin to get the parent of.

        Returns:
            The parent plugin or None if the plugin has no parent.

        Raises:
            PluginParentNotFoundError: If the plugin has a parent but it can not be found.
        """
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

    def ensure_parent(self, plugin: ProjectPlugin) -> ProjectPlugin:
        """Ensure that plugin has a parent set.

        Args:
            plugin: To set the parent of if necessary.

        Returns:
            The plugin (updated if necessary).
        """
        if not plugin.parent:
            plugin.parent = self.get_parent(plugin)

        return plugin
