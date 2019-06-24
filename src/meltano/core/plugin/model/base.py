from meltano.core.plugin import PluginInstall, PluginType


class ModelPlugin(PluginInstall):
    __plugin_type__ = PluginType.MODELS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
