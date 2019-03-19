from meltano.core.behavior.hookable import HookObject, hook
from meltano.core.plugin import Plugin, PluginType


class ModelPlugin(Plugin, HookObject):
    __plugin_type__ = PluginType.MODELS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
