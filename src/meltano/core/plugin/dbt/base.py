"""Defines DBT-specific plugins."""

from __future__ import annotations

import typing as t
from pathlib import Path

import structlog

from meltano.core.error import PluginInstallError
from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.transform_add_service import TransformAddService

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.plugin_install_service import PluginInstaller
    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


class DbtInvoker(PluginInvoker):
    """dbt plugin invoker."""

    def Popen_options(self):  # noqa: ANN201, N802
        """Get options for `subprocess.Popen`.

        Returns:
            Mapping of keyword arguments for `subprocess.Popen`.
        """
        return {**super().Popen_options(), "cwd": self.plugin_config["project_dir"]}


class DbtPlugin(BasePlugin):
    """dbt plugin."""

    __plugin_type__ = PluginType.TRANSFORMERS

    invoker_class = DbtInvoker


async def install_dbt_plugin(
    *,
    project: Project,
    plugin: ProjectPlugin,
    reason: PluginInstallReason,
    **kwargs,  # noqa: ANN003, ARG001
) -> None:
    """Install the transform into the project.

    Args:
        project: The Meltano project.
        plugin: The plugin to install into the specified project.
        reason: Install reason.
        kwargs: Unused additional arguments for the installation of the plugin.

    Raises:
        PluginInstallError: The plugin failed to install.
    """
    if reason not in {PluginInstallReason.ADD, PluginInstallReason.UPGRADE}:
        logger.info(
            f"Run `meltano add transform {plugin.name}` "  # noqa: G004
            "to re-add this transform to your dbt project.",
        )
        return

    try:
        transform_add_service = TransformAddService(project)

        # Add repo to my-test-project/transform/packages.yml
        packages_path = transform_add_service.packages_file.relative_to(project.root)
        logger.info(f"Adding dbt package '{plugin.pip_url}' to '{packages_path}'...")  # noqa: G004
        transform_add_service.add_to_packages(plugin)

        # Add model and vars to my-test-project/transform/dbt_project.yml
        dbt_project_path = transform_add_service.dbt_project_file.relative_to(
            project.root,
        )
        logger.info(f"Adding dbt model to '{dbt_project_path}'...")  # noqa: G004
        transform_add_service.update_dbt_project(plugin)
    except PluginNotFoundError as ex:
        raise PluginInstallError(  # noqa: TRY003
            "Transformer 'dbt' is not installed. "  # noqa: EM101
            "Run `meltano add transformer dbt` to add it to your project.",
        ) from ex
    except FileNotFoundError as ex:
        relative_path = Path(ex.filename).relative_to(project.root)
        raise PluginInstallError(  # noqa: TRY003
            f"File '{relative_path}' could not be found. "  # noqa: EM102
            "Run `meltano add files files-dbt` to set up a dbt project.",
        ) from ex


class DbtTransformPlugin(BasePlugin):
    """Plugin type for dbt transforms."""

    __plugin_type__ = PluginType.TRANSFORMS

    EXTRA_SETTINGS: t.ClassVar[list[SettingDefinition]] = [
        SettingDefinition(name="_package_name", value="$MELTANO_TRANSFORM_NAMESPACE"),
        SettingDefinition(name="_vars", kind=SettingKind.OBJECT, value={}),
    ]

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Initialize the `DbtTransformPlugin`.

        Args:
            args: Positional arguments passed to `BasePlugin`.
            kwargs: Keyword arguments passed to `BasePlugin`.
        """
        super().__init__(*args, **kwargs)
        self.installer: PluginInstaller = install_dbt_plugin

    def is_invokable(self) -> bool:
        """Return whether the plugin is invokable.

        Returns:
            Whether the plugin is invokable.
        """
        return False
