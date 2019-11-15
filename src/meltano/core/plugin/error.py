from . import PluginRef


class PluginMissingError(Exception):
    """
    Base exception when a plugin seems to be missing.
    """

    def __init__(self, plugin_or_name):
        if isinstance(plugin_or_name, PluginRef):
            self.plugin_name = plugin_or_name.name
        else:
            self.plugin_name = plugin_or_name

    def __str__(self):
        return f"The requested plugin '{self.plugin_name}' is missing."


class PluginExecutionError(Exception):
    """
    Base exception for problems that stems from the
    execution of a plugin (sub-process).
    """

    pass


class PluginLacksCapabilityError(Exception):
    """
    Base exception when a plugin lacks a requested capability
    """

    pass
