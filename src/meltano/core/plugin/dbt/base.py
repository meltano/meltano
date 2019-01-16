from meltano.core.behavior.hookable import HookObject, hook
from meltano.core.plugin import Plugin, PluginType


class DbtPlugin(Plugin, HookObject):
    __plugin_type__ = PluginType.TRANSFORMERS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)


class DbtTransformPlugin(Plugin, HookObject):
    __plugin_type__ = PluginType.TRANSFORMS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
