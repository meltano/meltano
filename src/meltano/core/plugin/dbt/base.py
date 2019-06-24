from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.plugin_invoker import PluginInvoker


class DbtPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMERS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    def invoker(self, session, project, *args, **kwargs):
        return DbtInvoker(
            session,
            project,
            self,
            *args,
            run_dir=project.root_dir("transform"),
            **kwargs
        )


class DbtTransformPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMS

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)


class DbtInvoker(PluginInvoker):
    def Popen_options(self):
        options = super().Popen_options()
        options["cwd"] = str(self.project.root_dir("transform"))

        return options
