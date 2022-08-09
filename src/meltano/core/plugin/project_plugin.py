"""Project Plugin Class."""

from __future__ import annotations

import copy
import logging
import sys
from typing import Any, Iterable

from meltano.core.plugin.requirements import PluginRequirement
from meltano.core.setting_definition import SettingDefinition
from meltano.core.utils import expand_env_vars, flatten, uniques_in

from .base import PluginDefinition, PluginRef, PluginType, Variant
from .command import Command
from .factory import base_plugin_factory

logger = logging.getLogger(__name__)


class CyclicInheritanceError(Exception):
    """Exception raised when project plugin inherits from itself cyclicly."""

    def __init__(self, plugin: ProjectPlugin, ancestor: ProjectPlugin):
        """Initialize cyclic inheritance error.

        Args:
            plugin: A ProjectPlugin
            ancestor: The given ProjectPlugins' ancestor.
        """
        super().__init__()

        self.plugin = plugin
        self.ancestor = ancestor

    def __str__(self):
        """Return error message.

        Returns:
            A formatted error message string.
        """
        return (
            "{type} '{name}' cannot inherit from '{ancestor}', "
            + "which itself inherits from '{name}'"
        ).format(
            type=self.plugin.type.descriptor.capitalize(),
            name=self.plugin.name,
            ancestor=self.ancestor.name,
        )


class ProjectPlugin(PluginRef):  # noqa: WPS230, WPS214 # too many attrs and methods
    """ProjectPlugin class."""

    VARIANT_ATTR = "variant"

    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        inherit_from: str | None = None,
        namespace: str | None = None,
        variant: str | None = None,
        pip_url: str | None = None,
        executable: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        requires: dict[PluginType, list] | None = None,
        config: dict | None = None,
        default_variant=Variant.ORIGINAL_NAME,
        env: dict[str, str] | None = None,
        **extras,
    ):
        """ProjectPlugin.

        Args:
            plugin_type: PluginType instance.
            name: Plugin name.
            inherit_from: Name of plugin to inherit from.
            namespace: Plugin namespace.
            variant: Plugin variant.
            pip_url: Plugin install pip url.
            executable: Executable name.
            capabilities: Capabilities.
            settings_group_validation: Settings group validation.
            settings: Settings.
            commands: Plugin commands.
            requires: Plugin requirements.
            config: Plugin configuration.
            default_variant: Default variant for this plugin.
            env: Environment variables to inject into plugins runtime context.
            extras: Extra keyword arguments.
        """
        super().__init__(plugin_type, name)

        # Attributes will be listed in meltano.yml in the order they are set on self:
        self.inherit_from = (
            inherit_from if inherit_from and inherit_from != name else None
        )

        # If a custom definition is provided, its properties will come before all others in meltano.yml
        self.custom_definition = None
        self._flattened.add("custom_definition")

        self._parent = None
        if not self.inherit_from and namespace:
            # When not explicitly inheriting, a namespace indicates an embedded custom plugin definition
            self.custom_definition = PluginDefinition(
                plugin_type,
                name,
                namespace,
                variant=variant,
                pip_url=pip_url,
                executable=executable,
                capabilities=capabilities,
                settings_group_validation=settings_group_validation,
                settings=settings,
                requires=requires,
                **extras,
            )

            # Any properties considered "extra" by the embedded plugin definition
            # should be considered extras of the project plugin, since they are
            # the current values, not default values.
            extras = self.custom_definition.extras
            self.custom_definition.extras = {}

            # Typically, the parent is set from ProjectPluginsService.current_plugins,
            # where we have access to the discoverable plugin definitions coming from
            # PluginDiscoveryService, but here we can set the parent directly.
            self.parent = base_plugin_factory(self.custom_definition, variant)

        # These properties are also set on the parent, but can be overridden
        self.namespace = namespace
        self.set_presentation_attrs(extras)
        self.variant = variant
        self.pip_url = pip_url
        self.executable = executable
        self.capabilities = capabilities
        self.settings_group_validation = settings_group_validation
        self.settings = list(map(SettingDefinition.parse, settings or []))
        self.commands = Command.parse_all(commands)
        self.requires = PluginRequirement.parse_all(requires)
        self.env = env or {}

        self._fallbacks.update(
            [
                "logo_url",
                "description",
                self.VARIANT_ATTR,
                "pip_url",
                "executable",
                "capabilities",
                "settings_group_validation",
            ]
        )

        # If no variant is set, we fall back on the default
        self._defaults[self.VARIANT_ATTR] = lambda _: default_variant

        if self.inherit_from:
            # When explicitly inheriting from a project plugin or discoverable definition,
            # derive default values from our own name
            self._defaults["namespace"] = lambda plugin: plugin.name.replace("-", "_")
            self._defaults["label"] = lambda plugin: (
                f"{plugin.parent.label}: {plugin.name}"
                if plugin.parent
                else plugin.name
            )
        else:
            # When shadowing a discoverable definition with the same name (no `inherit_from`),
            # or an embedded custom definition (with `namespace`), fall back on parent's
            # values derived from its name instead
            self._fallbacks.update(["namespace", "label"])

        self.config = copy.deepcopy(config or {})
        self.extras = extras

        if "profiles" in extras:
            logger.warning(
                "Plugin configuration profiles are no longer supported, ignoring "
                + f"`profiles` in '{name}' {plugin_type.descriptor} definition."
            )

    @property
    def parent(self) -> ProjectPlugin:
        """Plugins parent.

        Returns:
            Parent ProjectPlugin instance, or None if no parent.
        """
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        ancestor = new_parent
        while isinstance(ancestor, self.__class__):
            if ancestor == self:
                raise CyclicInheritanceError(self, ancestor)

            ancestor = ancestor.parent

        self._parent = new_parent
        self._fallback_to = new_parent

    @property
    def is_variant_set(self) -> bool:
        """Check if variant is set explicitly.

        Returns:
            'True' if variant is set explicitly.
        """
        return self.is_attr_set(self.VARIANT_ATTR)

    @property
    def info(self) -> dict[str, str]:
        """Plugin info dict.

        Returns:
            Dictionary of plugin info (name, namespace and variant)
        """
        return {"name": self.name, "namespace": self.namespace, "variant": self.variant}

    @property
    def info_env(self) -> dict[str, str]:
        """Plugin environment info.

        Returns:
            Dictionary of plugin info formatted as Meltano environment variables.
        """
        # MELTANO_EXTRACTOR_...
        return flatten({"meltano": {self.type.singular: self.info}}, "env_var")

    @property
    def all_commands(self) -> dict[str, Command]:
        """Return all commands for this plugin.

        Returns:
            Dictionary of supported commands, including those inherited from the parent plugin.
        """
        return {**self._parent.all_commands, **self.commands}

    @property
    def test_commands(self) -> dict[str, Command]:
        """Return the test commands for this plugin.

        Returns:
            Dictionary of supported test commands, including those inherited from the parent plugin.
        """
        return {
            name: command
            for name, command in self.all_commands.items()
            if name.startswith("test")
        }

    @property
    def supported_commands(self) -> list[str]:
        """Return supported command names.

        Returns:
            All defined command names for the plugin.
        """
        return list(self.all_commands.keys())

    def env_prefixes(self, for_writing=False) -> list[str]:
        """Return environment variable prefixes.

        Args:
            for_writing: Include parent prefix (used when writing to env vars)

        Returns:
            A list of env prefixes.
        """
        prefixes = [self.name, self.namespace]

        if for_writing:
            prefixes.extend(self._parent.env_prefixes(for_writing=True))
            prefixes.append(f"meltano_{self.type.verb}")  # MELTANO_EXTRACT_...

        return uniques_in(prefixes)

    @property
    def extra_config(self) -> dict[str, Any]:
        """Return plugin extra config.

        Returns:
            Dictionary of extra config.
        """
        return {f"_{key}": value for key, value in self.extras.items()}

    @property
    def config_with_extras(self) -> dict[str, Any]:
        """Return config with extras.

        Returns:
            Complete config dictionary, including config extras.
        """
        return {**self.config, **self.extra_config}

    @config_with_extras.setter
    def config_with_extras(self, new_config_with_extras):
        self.config.clear()
        self.extras.clear()

        for key, value in new_config_with_extras.items():
            if key.startswith("_"):
                self.extras[key[1:]] = value
            else:
                self.config[key] = value

    @property
    def all_settings(self) -> list[SettingDefinition]:
        """Return all settings for this plugin.

        Returns:
            List of settings, including those inherited from the parent plugin.
        """
        # New setting definitions override old ones
        new_setting_names = {setting.name for setting in self.settings}
        existing_settings = [
            setting
            for setting in self._parent.all_settings
            if setting.name not in new_setting_names
        ]
        existing_settings.extend(self.settings)

        return [
            *existing_settings,
            *SettingDefinition.from_missing(existing_settings, self.config),
        ]

    @property
    def extra_settings(self) -> list[SettingDefinition]:
        """Return extra settings.

        Returns:
            A list of extra SettingDefinitions, including those defined by the parent.
        """
        existing_settings = self._parent.extra_settings
        return [
            *existing_settings,
            *SettingDefinition.from_missing(existing_settings, self.extra_config),
        ]

    @property
    def settings_with_extras(self) -> list[SettingDefinition]:
        """Return all settings.

        Returns:
            A complete list of SettingDefinitions, including extras.
        """
        return [*self.all_settings, *self.extra_settings]

    def is_custom(self) -> bool:
        """Return if plugin is custom.

        Returns:
            'True' is plugin is custom.
        """
        return self.custom_definition is not None

    @property
    def is_shadowing(self) -> bool:
        """Return whether this plugin is shadowing a base plugin with the same name.

        Returns:
            'True' if this plugin is shadowing a base plugin with the same name.
        """
        return not self.inherit_from

    @property
    def formatted_pip_url(self) -> str:
        """Return the formatted version of the pip_url.

        Expands ${MELTANO__PYTHON_VERSION} to the major.minor version string of the current runtime.

        Returns:
            Expanded pip url string.
        """
        return expand_env_vars(
            self.pip_url,
            {
                "MELTANO__PYTHON_VERSION": f"{sys.version_info.major}.{sys.version_info.minor}"
            },
        )

    @property
    def venv_name(self) -> str:
        """Return the venv name this plugin should use.

        Returns:
            The name of this plugins parent if both pip urls are the same, else this plugins name.
        """
        if not self.inherit_from:
            return self.name

        if not self.pip_url or (self.parent.pip_url == self.pip_url):
            return self.parent.name

        return self.name

    def get_requirements(
        self,
        plugin_types: Iterable[PluginType] | None = None,
    ) -> dict[PluginType, list[PluginRequirement]]:
        """Return the requirements for this plugin.

        Args:
            plugin_types: The plugin types to include.

        Returns:
            A list of requirements for this plugin, optionally filtered for specified
            plugin types.
        """
        plugin_types = plugin_types or list(PluginType)
        plugins: dict[PluginType, list[PluginRequirement]] = {}

        for plugin_type in plugin_types:
            plugins[plugin_type] = [
                *self._parent.all_requires.get(plugin_type, []),
                *self.requires.get(plugin_type, []),
            ]

        return plugins

    @property
    def all_requires(self) -> dict[PluginType, list]:
        """Return all requires for this plugin.

        Returns:
            List of supported requires, including those inherited from the parent plugin.
        """
        return self.get_requirements(plugin_types=None)

    @property
    def requirements(self) -> list[ProjectPlugin]:
        """Return the requirements for this plugin.

        Returns:
            A list of requirements for this plugin.
        """
        return [
            ProjectPlugin(plugin_type=plugin_type, name=dep.name, variant=dep.variant)
            for plugin_type, deps in self.all_requires.items()
            for dep in deps
        ]
