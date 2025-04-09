"""Meltano enums."""

from __future__ import annotations

import enum
import sys
import typing as t

if sys.version_info < (3, 11):
    from backports.strenum import StrEnum
else:
    from enum import StrEnum

if t.TYPE_CHECKING:
    from ruamel.yaml import Node, Representer, ScalarNode


class LogFormat(StrEnum):
    """Log format options."""

    colored = enum.auto()
    uncolored = enum.auto()
    json = enum.auto()
    key_value = enum.auto()
    plain = enum.auto()


class Payload(enum.IntFlag):
    """Flag indicating whether a Job has state in its payload field."""

    STATE = 1
    INCOMPLETE_STATE = 2


class PluginAddedReason(StrEnum):
    """The reason why a plugin was added to the project."""

    #: The plugin was added by the user.
    USER_REQUEST = enum.auto()

    #: The plugin was added because it is related to another plugin.
    RELATED = enum.auto()

    #: The plugin was added because it is required by another plugin.
    REQUIRED = enum.auto()


class YAMLEnum(StrEnum):
    """Serializable Enum class."""

    @staticmethod
    def yaml_representer(dumper, obj) -> str:  # noqa: ANN001
        """Represent as yaml.

        Args:
            dumper: YAML dumper.
            obj: Object to dump.

        Returns:
            Object in yaml string form.
        """
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(obj))

    @classmethod
    def to_yaml(cls, representer: Representer, node: t.Any) -> ScalarNode:  # noqa: ANN401
        """Represent as yaml.

        Args:
            representer: YAML representer.
            node: Object to dump.

        Returns:
            Object in yaml string form.
        """
        return representer.represent_scalar("tag:yaml.org,2002:str", str(node))

    @classmethod
    def from_yaml(
        cls,
        constructor,  # noqa: ANN001, ARG003
        node: Node,
    ) -> YAMLEnum:
        """Construct from yaml.

        Args:
            constructor: Class constructor.
            node: YAML node.

        Returns:
            Object from yaml node.
        """
        return cls(node.value)


class PluginType(YAMLEnum):
    """The type of a plugin."""

    EXTRACTORS = enum.auto()
    LOADERS = enum.auto()
    TRANSFORMS = enum.auto()
    ORCHESTRATORS = enum.auto()
    TRANSFORMERS = enum.auto()
    FILES = enum.auto()
    UTILITIES = enum.auto()
    MAPPERS = enum.auto()
    MAPPINGS = enum.auto()

    @property
    def descriptor(self) -> str:
        """Return the descriptor of the plugin type.

        Returns:
            The descriptor of the plugin type.
        """
        return "file bundle" if self is self.__class__.FILES else self.singular

    @property
    def singular(self) -> str:
        """Make singular form for `meltano add PLUGIN_TYPE`.

        Returns:
            The singular form of the plugin type.
        """
        return "utility" if self is self.__class__.UTILITIES else self.value[:-1]

    @property
    def verb(self) -> str:
        """Make verb form.

        Returns:
            The verb form of the plugin type.
        """
        if self is self.__class__.TRANSFORMS:
            return self.singular
        if self is self.__class__.UTILITIES:
            return "utilize"
        return "map" if self is self.__class__.MAPPERS else self.value[:-3]

    @property
    def discoverable(self) -> bool:
        """Whether this plugin type is discoverable on the Hub.

        Returns:
            Whether this plugin type is discoverable on the Hub.
        """
        return self is not self.__class__.MAPPINGS

    @classmethod
    def value_exists(cls, value: str) -> bool:
        """Check if a plugin type exists.

        Args:
            value: The plugin type to check.

        Returns:
            True if the plugin type exists, False otherwise.
        """
        return value in cls._value2member_map_

    @classmethod
    def cli_arguments(cls) -> list:
        """Return the list of plugin types that can be used as CLI arguments.

        Returns:
            The list of plugin types that can be used as CLI arguments.
        """
        return [
            getattr(plugin_type, plugin_type_name)
            for plugin_type in cls
            for plugin_type_name in ("singular", "value")
        ]

    @classmethod
    def from_cli_argument(cls, value: str) -> PluginType:
        """Get the plugin type from a CLI argument.

        Args:
            value: The CLI argument.

        Returns:
            The plugin type.

        Raises:
            ValueError: If the plugin type does not exist.
        """
        for plugin_type in cls:
            if value in {plugin_type.value, plugin_type.singular}:
                return plugin_type

        raise ValueError(f"{value!r} is not a valid {cls.__name__}")  # noqa: EM102

    @classmethod
    def plurals(cls) -> list[str]:
        """Return the list of plugin plural names.

        Returns:
            The list of plugin plurals.
        """
        return [plugin_type.value for plugin_type in cls]
