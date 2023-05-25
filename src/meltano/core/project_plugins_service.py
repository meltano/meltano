"""Project plugin service."""


from __future__ import annotations

import enum
import sys
import typing as t
from contextlib import contextmanager, suppress

import structlog

from meltano.core.environment import EnvironmentPluginConfig
from meltano.core.error import MeltanoError
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.plugin.base import VariantNotFoundError
from meltano.core.plugin.error import PluginNotFoundError, PluginParentNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_discovery_service import (
    LockedDefinitionService,
    PluginDiscoveryService,
)
from meltano.core.plugin_lock_service import PluginLockService
from meltano.core.settings_service import FeatureFlags

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

if t.TYPE_CHECKING:
    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


class DefinitionSource(enum.Flag):
    """The source of a plugin definition."""

    NONE = 0
    DISCOVERY = enum.auto()
    HUB = enum.auto()
    CUSTOM = enum.auto()
    LOCKFILE = enum.auto()
    INHERITED = enum.auto()

    ANY = DISCOVERY | HUB | CUSTOM | LOCKFILE | INHERITED
    LOCAL = ~HUB


class PluginAlreadyAddedException(Exception):
    """Raised when a plugin is already added to the project."""

    def __init__(self, plugin: PluginRef, new_plugin: PluginRef):
        """Create a new Plugin Already Added Exception.

        Args:
            plugin: The plugin that was already added.
            new_plugin: The plugin that was attempted to be added.
        """
        self.plugin = plugin
        self.new_plugin = new_plugin
        super().__init__()


class PluginDefinitionNotFoundError(MeltanoError):
    """Raised when no plugin definition is found."""

    def __init__(
        self,
        plugin: ProjectPlugin,
        error: Exception | None,
        source: DefinitionSource,
    ):
        """Initialize a new error.

        Args:
            plugin: The plugin that was not found.
            error: The error that was raised, if any.
            source: The sources searched for the plugin.
        """
        reason = (
            str(error)
            if error
            else f"No definition found for {plugin.type.descriptor} {plugin.name}"
        )
        instruction = None

        if DefinitionSource.HUB in source:
            instruction = (
                f"Run `meltano discover {plugin.type.descriptor}` to explore available "
                "plugins"
            )
        else:
            instruction = (
                "Try running `meltano lock --update --all` to ensure your plugins are "
                "up to date"
            )

        super().__init__(reason=reason, instruction=instruction)


class ProjectPluginsService:  # noqa: WPS214, WPS230 (too many methods, attributes)
    """Project Plugins Service."""

    def __init__(self, project: Project):
        """Create a new Project Plugins Service.

        Args:
            project: The Meltano project.
        """
        self.project = project
        self.discovery_service = PluginDiscoveryService(project)
        self.lock_service = PluginLockService(project)
        self.locked_definition_service = LockedDefinitionService(project)
        with self.project.settings.feature_flag(
            FeatureFlags.PLUGIN_LOCKS_REQUIRED.value,
            raise_error=False,
        ) as flag:
            if flag:
                self._prefer_source = DefinitionSource.LOCAL
            else:
                self._prefer_source = DefinitionSource.ANY

    @cached_property
    def current_plugins(self):
        """Return the current plugins.

        Returns:
            The current plugins.
        """
        return self.project.config_service.current_meltano_yml.plugins

    @contextmanager
    def update_plugins(self):
        """Update the current plugins.

        Yields:
            The current plugins.
        """
        with self.project.config_service.update_meltano_yml() as meltano_yml:
            yield meltano_yml.plugins

    def add_to_file(self, plugin: ProjectPlugin):
        """Add plugin to `meltano.yml`.

        Args:
            plugin: The plugin to add.

        Raises:
            PluginAlreadyAddedException: If the plugin is already added.

        Returns:
            The added plugin.
        """
        # FIXME: `should_add_to_file` is a method from `BasePlugin`, which is
        #        not a subclass of `ProjectPlugin`. I've left this call to it
        #        in-place because I'm worried that removing it will break stuff
        #        that relies on it, but something is definitely wrong here.
        #        We default to `True` for `ProjectPlugin` objects.
        if not getattr(plugin, "should_add_to_file", lambda: True)():
            return plugin

        with suppress(PluginNotFoundError):
            existing_plugin = self.get_plugin(plugin)
            raise PluginAlreadyAddedException(existing_plugin, plugin)

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
        plugin_type: PluginType | None = None,
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
                "Plugin configuration profiles are no longer supported, "
                f"ignoring `@{profile_name}` in plugin name.",
            )

        try:
            plugin = next(
                plugin
                for plugin in self.plugins(ensure_parent=False)
                if (
                    plugin.name == plugin_name  # noqa: WPS222 (with too much logic)
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
                PluginRef(plugin_type, plugin_name) if plugin_type else plugin_name,
            ) from stop

    def find_plugin_by_namespace(
        self,
        plugin_type: PluginType,
        namespace: str,
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

    def find_plugins_by_mapping_name(self, mapping_name: str) -> list[ProjectPlugin]:
        """Find plugins with the specified mapping name in their mappings config.

        Args:
            mapping_name: The name of the mapping to find.

        Returns:
            The mapping plugins with the specified mapping name.

        Raises:
            PluginNotFoundError: If no mapper plugin with the specified mapping
                name is found.
        """
        found: list[ProjectPlugin] = []
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
        self,
        plugin_type: PluginType,
        ensure_parent=True,
    ) -> list[ProjectPlugin]:
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
                plugin_type,
                ensure_parent=ensure_parent,
            )
            for plugin_type in PluginType
        }

    def plugins(self, ensure_parent=True) -> t.Generator[ProjectPlugin, None, None]:
        """Return all plugins.

        Args:
            ensure_parent: If True, ensure that plugin has a parent plugin set.

        Yields:
            Plugins.
        """
        yield from (
            plugin
            for _, plugins in self.plugins_by_type(ensure_parent=ensure_parent).items()
            for plugin in plugins
        )

    def update_plugin(self, plugin: ProjectPlugin):
        """Update a plugin.

        Args:
            plugin: The plugin to update.

        Returns:
            The outdated plugin.
        """
        with self.update_plugins() as plugins:
            # find the proper plugin to update
            idx, outdated = next(
                (idx, plg)
                for idx, plg in enumerate(plugins[plugin.type])
                if plg == plugin
            )

            plugins[plugin.type][idx] = plugin

            return outdated

    def update_environment_plugin(self, plugin: EnvironmentPluginConfig):
        """Update a plugin configuration inside a Meltano environment.

        Args:
            plugin: The plugin configuration to update.
        """
        with self.project.config_service.update_active_environment() as environment:
            environment.config.plugins.setdefault(plugin.type, [])

            # find the proper plugin to update
            p_idx, p_outdated = next(
                (
                    (idx, plg)
                    for idx, plg in enumerate(environment.config.plugins[plugin.type])
                    if plg == plugin
                ),
                (None, None),
            )

            if p_idx is None:
                environment.config.plugins.setdefault(plugin.type, [])
                environment.config.plugins[plugin.type].append(plugin)
            else:
                environment.config.plugins[plugin.type][p_idx] = plugin

    def _get_parent_from_discovery(self, plugin: ProjectPlugin) -> ProjectPlugin:
        """Get the parent plugin from discovery.yml.

        Args:
            plugin: The plugin to get the parent of.

        Returns:
            The parent plugin.

        Raises:
            PluginParentNotFoundError: If the parent plugin is not found.
        """
        try:
            return self.discovery_service.get_base_plugin(plugin)
        except (PluginNotFoundError, VariantNotFoundError) as err:
            if plugin.inherit_from:
                raise PluginParentNotFoundError(plugin, err) from err
            raise

    def _get_parent_from_hub(self, plugin: ProjectPlugin) -> ProjectPlugin:
        """Get the parent plugin from the hub.

        Args:
            plugin: The plugin to get the parent of.

        Returns:
            The parent plugin.

        Raises:
            PluginParentNotFoundError: If the parent plugin is not found.
        """
        try:
            return self.project.hub_service.get_base_plugin(
                plugin,
                variant_name=plugin.variant,
            )
        except PluginNotFoundError as err:
            if plugin.inherit_from:
                raise PluginParentNotFoundError(plugin, err) from err
            raise

    def find_parent(
        self,
        plugin: ProjectPlugin,
    ) -> tuple[ProjectPlugin, DefinitionSource]:
        """Find the parent plugin of a plugin.

        Args:
            plugin: The plugin to find the parent of.

        Returns:
            The parent plugin and the source of the parent.

        Raises:
            PluginDefinitionNotFoundError: If the parent plugin is not found.
        """
        error = None
        if (
            plugin.inherit_from
            and not plugin.is_variant_set
            and DefinitionSource.INHERITED in self._prefer_source
        ):
            try:
                return (
                    self.find_plugin(
                        plugin_type=plugin.type,
                        plugin_name=plugin.inherit_from,
                    ),
                    DefinitionSource.INHERITED,
                )
            except PluginNotFoundError as inherited_exc:
                error = inherited_exc

        if DefinitionSource.LOCKFILE in self._prefer_source:
            try:
                return (
                    self.locked_definition_service.get_base_plugin(
                        plugin,
                        variant_name=plugin.variant,
                    ),
                    DefinitionSource.LOCKFILE,
                )
            except PluginNotFoundError as lockfile_exc:
                error = lockfile_exc

        if DefinitionSource.DISCOVERY in self._prefer_source:
            try:
                return (
                    self._get_parent_from_discovery(plugin),
                    DefinitionSource.DISCOVERY,
                )
            except Exception as discovery_exc:
                error = discovery_exc

        if DefinitionSource.HUB in self._prefer_source:
            try:
                return (self._get_parent_from_hub(plugin), DefinitionSource.HUB)
            except Exception as hub_exc:
                error = hub_exc

        raise PluginDefinitionNotFoundError(
            plugin,
            error,
            self._prefer_source,
        ) from error

    def get_parent(self, plugin: ProjectPlugin) -> ProjectPlugin:
        """Get plugin's parent plugin.

        Args:
            plugin: The plugin to get the parent of.

        Returns:
            The parent plugin or None if the plugin has no parent.
        """
        parent, source = self.find_parent(plugin)

        logger.debug(
            "Found plugin parent",
            plugin=plugin.name,
            parent=parent.name,
            source=source,
        )
        return parent

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

    def get_transformer(self) -> ProjectPlugin:
        """Get first available Transformer plugin.

        Raises:
            PluginNotFoundError: If there is no transformer.

        Returns:
            First available transformer plugin.
        """
        transformer = next(
            iter(self.get_plugins_of_type(plugin_type=PluginType.TRANSFORMERS)),
            None,
        )
        if not transformer:
            raise PluginNotFoundError("No Plugin of type Transformer found.")
        return transformer

    @contextmanager
    def use_preferred_source(self, source: DefinitionSource) -> None:
        """Prefer a source of definition.

        Args:
            source: The source to prefer.

        Yields:
            None.
        """
        previous = self._prefer_source
        self._prefer_source = source
        yield
        self._prefer_source = previous
