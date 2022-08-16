"""Meltano file plugin type."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from meltano.core.behavior.hookable import hook
from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.venv_service import VirtualEnv

if TYPE_CHECKING:
    from os import PathLike
    from pathlib import Path

    from meltano.core.project import Project


logger = structlog.getLogger(__name__)


class FilePlugin(BasePlugin):
    """Meltano file plugin type."""

    __plugin_type__ = PluginType.FILES

    EXTRA_SETTINGS = [
        SettingDefinition(
            name="_update", kind=SettingKind.OBJECT, aliases=["update"], value={}
        )
    ]

    def is_invokable(self) -> bool:
        """Return whether the plugin is invokable.

        Returns:
            True if the plugin is invokable, False otherwise.
        """
        return False

    def should_add_to_file(self) -> bool:
        """Return whether the plugin should be added to `meltano.yml`.

        Returns:
            True if the plugin should be added to `meltano.yml`, False otherwise.
        """
        return len(self.extras.get("update", [])) > 0

    def file_contents(self, project: Project) -> dict[Path, str]:
        """Return the contents of the files to be created or updated.

        Args:
            project: The Meltano project.

        Returns:
            A dictionary of file names and their contents.
        """
        venv = VirtualEnv(project.plugin_dir(self, "venv"))
        bundle_dir = venv.site_packages_dir.joinpath("bundle")

        return {
            path.relative_to(bundle_dir): path.read_text()
            for path in bundle_dir.glob("**/*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path != bundle_dir.joinpath("__init__.py")
        }

    def update_file_header(self, relative_path: PathLike) -> str:
        """Return the header to be added to the top of the file.

        Args:
            relative_path: The relative path of the file.

        Returns:
            The header to be added to the top of the file.
        """
        return "\n".join(
            (
                f"# This file is managed by the '{self.name}' {self.type.descriptor} and updated automatically when `meltano upgrade` is run.",
                f"# To prevent any manual changes from being overwritten, remove the {self.type.descriptor} from `meltano.yml` or disable automatic updates:",
                f"#     meltano config --plugin-type={self.type} {self.name} set _update {relative_path} false",
            )
        )

    def project_file_contents(
        self,
        project: Project,
        paths_to_update: list[str],
    ) -> dict[Path, str]:
        """Return the contents of the files to be created or updated in the project.

        Args:
            project: The Meltano project.
            paths_to_update: The paths of the files to be updated.

        Returns:
            A dictionary of file names and their contents.
        """

        def with_update_header(content: str, relative_path: PathLike):
            if any(relative_path.match(path) for path in paths_to_update):
                content = "\n\n".join([self.update_file_header(relative_path), content])

            return content

        return {
            relative_path: with_update_header(content, relative_path)
            for relative_path, content in self.file_contents(project).items()
        }

    def write_file(
        self,
        project: Project,
        relative_path: PathLike,
        content: str,
    ) -> bool:
        """Write the file to the project.

        Args:
            project: The Meltano project.
            relative_path: The relative path of the file.
            content: The contents of the file.

        Returns:
            True if the file was written, False otherwise.
        """
        project_path = project.root_dir(relative_path)
        if project_path.exists() and project_path.read_text() == content:
            return False

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.write_text(content)

        return True

    def write_files(
        self,
        project: Project,
        files_content: dict[Path, str],
    ) -> list[Path]:
        """Write the files to the project.

        Args:
            project: The Meltano project.
            files_content: A dictionary of file names and their contents.

        Returns:
            A list of the paths of the files that were written.
        """
        return [
            relative_path
            for relative_path, content in files_content.items()
            if self.write_file(project, relative_path, content)
        ]

    def files_to_create(
        self,
        project: Project,
        paths_to_update: list[str],
    ) -> dict[Path, str]:
        """Return the contents of the files to be created in the project.

        Args:
            project: The Meltano project.
            paths_to_update: The paths of the files to be updated.

        Returns:
            A dictionary of file names and their contents.
        """

        def rename_if_exists(relative_path: Path):
            if not project.root_dir(relative_path).exists():
                return relative_path

            logger.info(
                f"File {str(relative_path)!r} already exists, keeping both versions"
            )
            return relative_path.with_name(
                f"{relative_path.stem} ({self.name}){relative_path.suffix}"
            )

        return {
            rename_if_exists(relative_path): content
            for relative_path, content in self.project_file_contents(
                project, paths_to_update
            ).items()
        }

    def files_to_update(
        self,
        project: Project,
        paths_to_update: list[str],
    ) -> dict[Path, str]:
        """Return the contents of the files to be updated in the project.

        Args:
            project: The Meltano project.
            paths_to_update: The paths of the files to be updated.

        Returns:
            A dictionary of file names and their contents.
        """
        file_contents = self.project_file_contents(project, paths_to_update)
        return {
            relative_path: content
            for relative_path, content in file_contents.items()
            if any(relative_path.match(path) for path in paths_to_update)
        }

    def create_files(
        self,
        project: Project,
        paths_to_update: list[str] | None = None,
    ) -> list[Path]:
        """Create the files in the project.

        Args:
            project: The Meltano project.
            paths_to_update: Optional paths of the files to be updated.

        Returns:
            A list of the paths of the files that were created.
        """
        return self.write_files(
            project,
            self.files_to_create(
                project, [] if paths_to_update is None else paths_to_update
            ),
        )

    def update_files(
        self,
        project: Project,
        paths_to_update: list[str] | None = None,
    ) -> list[Path]:
        """Update the files in the project.

        Args:
            project: The Meltano project.
            paths_to_update: Optional paths of the files to be updated.

        Returns:
            A list of the paths of the files that were updated.
        """
        return self.write_files(
            project,
            self.files_to_update(
                project, [] if paths_to_update is None else paths_to_update
            ),
        )

    @hook("after_install")
    async def after_install(
        self,
        installer: PluginInstallService,
        plugin: ProjectPlugin,
        reason: PluginInstallReason,
    ):
        """Trigger after install tasks.

        Args:
            installer: The plugin installer.
            plugin: The installed plugin.
            reason: The reason for the installation.
        """
        project = installer.project
        plugins_service = installer.plugins_service

        plugin_settings_service = PluginSettingsService(
            project, plugin, plugins_service=plugins_service
        )
        update_config = plugin_settings_service.get("_update")
        paths_to_update = [
            path for path, to_update in update_config.items() if to_update
        ]

        if reason is PluginInstallReason.ADD:
            logger.info(f"Adding '{plugin.name}' files to project...")

            for path in self.create_files(project, paths_to_update):
                logger.info(f"Created {path}")
        elif reason is PluginInstallReason.UPGRADE:
            logger.info(f"Updating '{plugin.name}' files in project...")

            updated_paths = self.update_files(project, paths_to_update)
            if not updated_paths:
                logger.info("Nothing to update")
                return

            for path in updated_paths:
                logger.info(f"Updated {path}")
        else:
            logger.info(
                f"Run `meltano upgrade files` to update your project's '{plugin.name}' files."
            )
