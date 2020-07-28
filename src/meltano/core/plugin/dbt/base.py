from pathlib import Path

from meltano.core.plugin import PluginInstall, PluginRef, PluginType
from meltano.core.error import PluginInstallError
from meltano.core.plugin.error import PluginMissingError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition
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

    def install(self, reason):
        if reason in (PluginInstallReason.ADD, PluginInstallReason.UPGRADE):
            try:
                transform_add_service = TransformAddService(self.project)

                # Add repo to my-test-project/transform/packages.yml
                packages_path = transform_add_service.packages_file.relative_to(
                    self.project.root
                )
                print(
                    f"Adding dbt package '{self.plugin.pip_url}' to '{packages_path}'..."
                )
                transform_add_service.add_to_packages(self.plugin)

                # Add model and vars to my-test-project/transform/dbt_project.yml
                dbt_project_path = transform_add_service.dbt_project_file.relative_to(
                    self.project.root
                )
                print(f"Adding dbt model to '{dbt_project_path}'...")
                transform_add_service.update_dbt_project(self.plugin)
            except PluginMissingError:
                raise PluginInstallError(
                    "Transformer 'dbt' is not installed. Run `meltano add transformer dbt` to add it to your project."
                )
            except FileNotFoundError as err:
                relative_path = Path(err.filename).relative_to(self.project.root)
                raise PluginInstallError(
                    f"File {relative_path}' could not be found. Run `meltano add files dbt` to set up a dbt project."
                )
        else:
            print(
                f"Run `meltano add transform {self.plugin.name}` to re-add this transform to your dbt project."
            )


class DbtTransformPlugin(PluginInstall):
    __plugin_type__ = PluginType.TRANSFORMS
    __installer_cls__ = DbtTransformPluginInstaller

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

    def is_invokable(self):
        return False

    @property
    def runner(self):
        return PluginRef(PluginType.TRANSFORMERS, "dbt")

    @property
    def extra_settings(self):
        return [SettingDefinition(name="_vars", kind="object", value={})]
