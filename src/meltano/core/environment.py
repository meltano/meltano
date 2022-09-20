"""Meltano runtime environments."""

from __future__ import annotations

import copy
from typing import Any, Iterable, TypeVar

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginType
from meltano.core.plugin.base import PluginRef
from meltano.core.setting_definition import SettingDefinition
from meltano.core.state_service import STATE_ID_COMPONENT_DELIMITER
from meltano.core.utils import NotFound

TEnv = TypeVar("TEnv")


class NoActiveEnvironment(Exception):  # noqa: N818
    """Exception raised when invocation has no active environment."""


class EnvironmentNameContainsStateIdDelimiterError(Exception):
    """Occurs when an environment name contains the state ID component delimiter string."""

    def __init__(self, name: str):
        """Create a new exception.

        Args:
            name: The name of the environment.
        """
        super().__init__(
            f"The environment name '{name}' cannot contain the state ID component delimiter string '{STATE_ID_COMPONENT_DELIMITER}'"
        )


class EnvironmentPluginConfig(PluginRef):
    """Environment configuration for a plugin."""

    def __init__(
        self,
        plugin_type: PluginType,
        name: str,
        config: dict | None = None,
        env: dict | None = None,
        **extras,
    ):
        """Create a new plugin configuration object.

        Args:
            plugin_type: Extractor, loader, etc.
            name: Name of the plugin.
            config: Plugin configuration.
            env: Plugin environment variables.
            extras: Plugin extras.
        """
        super().__init__(plugin_type, name)
        self.config = copy.deepcopy(config or {})
        self.env = copy.deepcopy(env or {})
        self.extras = extras

    @property
    def extra_config(self):
        """Get extra config from the Meltano environment, like `select` and `schema`.

        Returns:
            Extra config.
        """
        return {f"_{key}": value for key, value in self.extras.items()}

    @property
    def config_with_extras(self):
        """Get plugin configuration values from the Meltano environment.

        Returns:
            Plugin configuration with extra values.
        """
        return {**self.config, **self.extra_config}

    @config_with_extras.setter
    def config_with_extras(self, new_config_with_extras: dict[str, Any]):
        """Set plugin configuration values from the Meltano environment.

        Args:
            new_config_with_extras: New plugin configuration with extra values.
        """
        self.config.clear()
        self.extras.clear()

        for key, value in new_config_with_extras.items():
            if key.startswith("_"):
                self.extras[key[1:]] = value
            else:
                self.config[key] = value

    def get_orphan_settings(
        self, existing: Iterable[SettingDefinition]
    ) -> list[SettingDefinition]:
        """Get orphan settings for this plugin.

        Orphan settings are `config` entries that do not have a
        matching parent entry within `settings`.

        Args:
            existing: Existing settings.

        Returns:
            List of orphan settings.
        """
        return SettingDefinition.from_missing(existing, self.config_with_extras)


class EnvironmentConfig(Canonical):
    """Meltano environment configuration."""

    def __init__(self, plugins: dict[str, list[dict]] = None, **extras):
        """Create a new environment configuration.

        Args:
            plugins: Mapping of plugin types to arrays of plugin configurations.
            extras: Environment extras.
        """
        super().__init__(extras=extras)
        self.plugins = self.load_plugins(plugins or {})

    def load_plugins(
        self,
        plugins: dict[str, list[dict]],
    ) -> dict[PluginType, list[EnvironmentPluginConfig]]:
        """Create plugin configurations from raw dictionary.

        Args:
            plugins: Plugin configurations.

        Returns:
            A mapping of plugin type to arrays of plugin configurations.
        """
        plugin_mapping = {}
        for raw_plugin_type, raw_plugins in plugins.items():
            plugin_type = PluginType(raw_plugin_type)
            plugin_mapping[plugin_type] = [
                EnvironmentPluginConfig(plugin_type=plugin_type, **raw_plugin)
                for raw_plugin in raw_plugins
            ]

        return plugin_mapping


class Environment(NameEq, Canonical):
    """Runtime environment for Meltano runs."""

    def __init__(
        self,
        name: str,
        config: dict | None = None,
        env: dict | None = None,
        state_id_suffix: str | None = None,
    ) -> None:
        """Create a new environment object.

        Args:
            name: Environment name. Must be unique.
            config: Dictionary with environment configuration.
            env: Optional override environment values.
            state_id_suffix: State ID suffix to use.

        Raises:
            EnvironmentNameContainsStateIdDelimiterError: If the name contains the state ID component delimiter string.
        """
        if STATE_ID_COMPONENT_DELIMITER in name:
            raise EnvironmentNameContainsStateIdDelimiterError(name)

        super().__init__()

        self.name = name
        self.config = EnvironmentConfig(**(config or {}))
        self.env = env or {}
        self.state_id_suffix = state_id_suffix

    @classmethod
    def find(cls: type[TEnv], objects: Iterable[TEnv], name: str) -> TEnv:
        """Lookup an environment by name from an iterable.

        Args:
            objects: Iterable of objects to search.
            name: Environment name.

        Returns:
            Environment object if found.

        Raises:
            NotFound: If an environment is not found.
        """
        try:
            return next(env for env in objects if env.name == name)
        except StopIteration as stop:
            raise NotFound(name, cls) from stop

    def get_plugin_config(
        self,
        plugin_type: PluginType,
        name: str,
    ) -> EnvironmentPluginConfig:
        """Get configuration for a plugin in this environment.

        Args:
            plugin_type: Extractor, loader, etc.
            name: Plugin name.

        Returns:
            A plugin configuration object if one is present in this environment.
        """
        default = EnvironmentPluginConfig(plugin_type, name)

        return next(
            filter(
                lambda plugin: plugin.name == name,
                self.config.plugins.get(plugin_type, []),
            ),
            default,
        )
