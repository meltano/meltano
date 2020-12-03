from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin


class ModelPlugin(ProjectPlugin):
    __plugin_type__ = PluginType.MODELS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
