from . import PluginInstall, PluginType


class ConnectionPlugin(PluginInstall):
    __plugin_type__ = PluginType.CONNECTIONS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
