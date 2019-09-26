from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.plugin_invoker import PluginInvoker


class DbtInvoker(PluginInvoker):
    def __init__(self, project, plugin, **kwargs):
        kwargs["run_dir"] = project.root_dir("transform")
        return super().__init__(project, plugin, **kwargs)

    def Popen_options(self):
        options = super().Popen_options()
        options["cwd"] = str(self.project.root_dir("transform"))

        return options


class DbtPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMERS
    __invoker_cls__ = DbtInvoker

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)


class DbtTransformPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)
