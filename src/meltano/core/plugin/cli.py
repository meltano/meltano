from meltano.core.plugin import BasePlugin, PluginType


class CliPlugin(BasePlugin):
    __plugin_type__ = PluginType.CLIS
