"""Defines DBT-specific plugins."""
from __future__ import annotations

import logging
from pathlib import Path

from meltano.core.error import PluginInstallError
from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.transform_add_service import TransformAddService

logger = logging.getLogger(__name__)


class DbtInvoker(PluginInvoker):
    def Popen_options(self):  # noqa: N802
        return {**super().Popen_options(), "cwd": self.plugin_config["project_dir"]}


class DbtPlugin(BasePlugin):
    __plugin_type__ = PluginType.TRANSFORMERS

    invoker_class = DbtInvoker


class DbtTransformPluginInstaller:
    def __init__(self, project, plugin: ProjectPlugin):
        self.project = project
        self.plugin = plugin

    async def install(self, reason, clean):
        """Install the transform into the project."""
        if reason not in {PluginInstallReason.ADD, PluginInstallReason.UPGRADE}:
            logger.info(
                f"Run `meltano add transform {self.plugin.name}` to re-add this transform to your dbt project."
            )
            return

        try:
            transform_add_service = TransformAddService(self.project)

            # Add repo to my-test-project/transform/packages.yml
            packages_path = transform_add_service.packages_file.relative_to(
                self.project.root
            )
            logger.info(
                f"Adding dbt package '{self.plugin.pip_url}' to '{packages_path}'..."
            )
            transform_add_service.add_to_packages(self.plugin)

            # Add model and vars to my-test-project/transform/dbt_project.yml
            dbt_project_path = transform_add_service.dbt_project_file.relative_to(
                self.project.root
            )
            logger.info(f"Adding dbt model to '{dbt_project_path}'...")
            transform_add_service.update_dbt_project(self.plugin)
        except PluginNotFoundError:
            raise PluginInstallError(
                "Transformer 'dbt' is not installed. Run `meltano add transformer dbt` to add it to your project."
            )
        except FileNotFoundError as err:
            relative_path = Path(err.filename).relative_to(self.project.root)
            raise PluginInstallError(
                f"File {relative_path}' could not be found. Run `meltano add files files-dbt` to set up a dbt project."
            )


class DbtTransformPlugin(BasePlugin):
    __plugin_type__ = PluginType.TRANSFORMS

    installer_class = DbtTransformPluginInstaller

    EXTRA_SETTINGS = [
        SettingDefinition(name="_package_name", value="$MELTANO_TRANSFORM_NAMESPACE"),
        SettingDefinition(name="_vars", kind=SettingKind.OBJECT, value={}),
    ]

    def is_invokable(self):
        return False
