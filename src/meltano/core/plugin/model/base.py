from meltano.core.plugin import BasePlugin, PluginType


class ModelPlugin(BasePlugin):
    __plugin_type__ = PluginType.MODELS
