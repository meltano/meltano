from __future__ import annotations  # noqa: D100

import inspect

from meltano.core.plugin.base import PluginDefinition

from . import PluginRef


class PluginNotFoundError(Exception):
    """Base exception when a plugin could not be found."""

    def __init__(self, plugin_or_name: PluginRef | str) -> None:  # noqa: D107
        if isinstance(plugin_or_name, PluginRef):
            self.plugin_type = plugin_or_name.type.descriptor
            self.plugin_name = plugin_or_name.name
        else:
            self.plugin_type = "plugin"
            self.plugin_name = plugin_or_name

    def __str__(self) -> str:  # noqa: D105
        return (
            f"{self.plugin_type.capitalize()} '{self.plugin_name}' is not "
            "known to Meltano"
        )


class PluginParentNotFoundError(Exception):
    """Base exception when a plugin's parent could not be found."""

    def __init__(self, plugin: PluginRef, parent_not_found_error: Exception) -> None:
        """Initialize exception for when plugin's parent could not be found."""
        self.plugin = plugin
        self.parent_not_found_error = parent_not_found_error

    def __str__(self) -> str:  # noqa: D105
        return (
            f"Could not find parent plugin for {self.plugin.type.descriptor} "
            f"'{self.plugin.name}': {self.parent_not_found_error}"
        )


class PluginNotSupportedError(Exception):
    """Base exception when a plugin is not supported for some operation."""

    def __init__(self, plugin: PluginRef):
        """Construct a PluginNotSupportedError instance."""
        self.plugin = plugin

    def __str__(self) -> str:  # noqa: D105
        return (
            "Operation not supported for "
            f"{self.plugin.type.descriptor} '{self.plugin.name}'"
        )


class PluginExecutionError(Exception):
    """Error stemming from the execution of a plugin (sub-process)."""


class PluginLacksCapabilityError(Exception):
    """Base exception when a plugin lacks a requested capability."""


class InvalidPluginDefinitionError(Exception):
    """Base exception when a plugin definition is invalid."""

    def __init__(self, definition: dict | None = None) -> None:
        """Construct a new "InvalidPluginDefinitionError instance.

        Args:
            definition: Plugin definition.
        """
        fullargspec = inspect.getfullargspec(PluginDefinition.__init__)
        _, _plugin_type, *required_properties = fullargspec.args

        if isinstance(definition, dict):
            missing_properties = ", ".join(
                [p for p in required_properties if p not in definition],
            )
            self.reason = f"missing properties ({missing_properties})"
        else:
            self.reason = "incorrect format"

    def __str__(self) -> str:  # noqa: D105
        return f"Plugin definition is invalid: {self.reason}"
