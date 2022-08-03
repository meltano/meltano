from __future__ import annotations

from . import PluginRef


class PluginNotFoundError(Exception):
    """Base exception when a plugin could not be found."""

    def __init__(self, plugin_or_name):
        if isinstance(plugin_or_name, PluginRef):
            self.plugin_type = plugin_or_name.type.descriptor
            self.plugin_name = plugin_or_name.name
        else:
            self.plugin_type = "plugin"
            self.plugin_name = plugin_or_name

    def __str__(self):
        return f"{self.plugin_type.capitalize()} '{self.plugin_name}' is not known to Meltano"


class PluginParentNotFoundError(Exception):
    """Base exception when a plugin's parent could not be found."""

    def __init__(self, plugin, parent_not_found_error):
        """Initialize exception for when plugin's parent could not be found."""
        self.plugin = plugin
        self.parent_not_found_error = parent_not_found_error

    def __str__(self):
        return "Could not find parent plugin for {type} '{name}': {error}".format(
            type=self.plugin.type.descriptor,
            name=self.plugin.name,
            error=self.parent_not_found_error,
        )


class PluginNotSupportedError(Exception):
    """Base exception when a plugin is not supported for some operation."""

    def __init__(self, plugin: PluginRef):
        """Construct a PluginNotSupportedError instance."""
        self.plugin = plugin

    def __str__(self):
        return f"Operation not supported for {self.plugin.type.descriptor} '{self.plugin.name}'"


class PluginExecutionError(Exception):
    """Base exception for problems that stem from the execution of a plugin (sub-process)."""


class PluginLacksCapabilityError(Exception):
    """Base exception when a plugin lacks a requested capability."""
