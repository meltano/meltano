from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.transform_add_service import TransformAddService
from meltano.core.behavior.hookable import hook


class DbtInvoker(PluginInvoker):
    def Popen_options(self):
        return {**super().Popen_options(), "cwd": self.plugin_config["project_dir"]}


class DbtPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMERS
    __invoker_cls__ = DbtInvoker

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)


class DbtTransformPluginInstaller:
    def __init__(self, project, plugin):
        self.project = project
        self.plugin = plugin

    def install(self):
        # Add repo to my-test-project/transform/packages.yml
        transform_add_service = TransformAddService(self.project)
        transform_add_service.add_to_packages(self.plugin)

        # Add model and vars to my-test-project/transform/dbt_project.yml
        transform_add_service.update_dbt_project(self.plugin)


class DbtTransformPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMS
    __installer_cls__ = DbtTransformPluginInstaller

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    def is_invokable(self):
        return False

    def is_configurable(self):
        return False
