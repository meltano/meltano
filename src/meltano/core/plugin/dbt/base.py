from pathlib import Path

from meltano.core.behavior.hookable import hook
from meltano.core.error import PluginInstallError
from meltano.core.plugin import BasePlugin, PluginRef, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.transform_add_service import TransformAddService


class DbtInvoker(PluginInvoker):
    def Popen_options(self):
        return {**super().Popen_options(), "cwd": self.plugin_config["project_dir"]}


class DbtPlugin(BasePlugin):
    __plugin_type__ = PluginType.TRANSFORMERS

    invoker_class = DbtInvoker


class DbtTransformPluginInstaller:
    def __init__(self, project, plugin: ProjectPlugin):
        self.project = project
        self.plugin = plugin

    async def install(self, reason):
        """Install the transform into the project."""
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
            except PluginNotFoundError:
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


class DbtTransformPlugin(BasePlugin):
    __plugin_type__ = PluginType.TRANSFORMS

    installer_class = DbtTransformPluginInstaller

    EXTRA_SETTINGS = [
        SettingDefinition(name="_package_name", value="$MELTANO_TRANSFORM_NAMESPACE"),
        SettingDefinition(name="_vars", kind=SettingKind.OBJECT, value={}),
    ]

    @property
    def runner(self):
        return PluginRef(PluginType.TRANSFORMERS, "dbt")

    def is_invokable(self):
        return False
