import logging
from pathlib import Path

from meltano.core.behavior.hookable import hook
from meltano.core.db import project_engine
from meltano.core.plugin import BasePlugin, PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_install_service import (
    PluginInstallReason,
    PluginInstallService,
)
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.venv_service import VirtualEnv


class FilePlugin(BasePlugin):
    __plugin_type__ = PluginType.FILES

    EXTRA_SETTINGS = [
        SettingDefinition(
            name="_update", kind=SettingKind.OBJECT, aliases=["update"], value={}
        )
    ]

    def is_invokable(self):
        return False

    def should_add_to_file(self):
        return len(self.extras.get("update", [])) > 0

    def file_contents(self, project):
        venv = VirtualEnv(project.plugin_dir(self, "venv"))
        bundle_dir = venv.site_packages_dir.joinpath("bundle")

        return {
            path.relative_to(bundle_dir): path.read_text()
            for path in bundle_dir.glob("**/*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path != bundle_dir.joinpath("__init__.py")
        }

    def update_file_header(self, relative_path):
        return "\n".join(
            [
                f"# This file is managed by the '{self.name}' {self.type.descriptor} and updated automatically when `meltano upgrade` is run.",
                f"# To prevent any manual changes from being overwritten, remove the {self.type.descriptor} from `meltano.yml` or disable automatic updates:",
                f"#     meltano config --plugin-type={self.type} {self.name} set _update {relative_path} false",
            ]
        )

    def project_file_contents(self, project, paths_to_update):
        def with_update_header(content, relative_path):
            if str(relative_path) in paths_to_update:
                content = "\n\n".join([self.update_file_header(relative_path), content])

            return content

        return {
            relative_path: with_update_header(content, relative_path)
            for relative_path, content in self.file_contents(project).items()
        }

    def write_file(self, project, relative_path, content):
        project_path = project.root_dir(relative_path)
        if project_path.exists() and project_path.read_text() == content:
            return False

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.write_text(content)

        return True

    def write_files(self, project, files_content):
        return [
            relative_path
            for relative_path, content in files_content.items()
            if self.write_file(project, relative_path, content)
        ]

    def files_to_create(self, project, paths_to_update):
        def rename_if_exists(relative_path):
            if not project.root_dir(relative_path).exists():
                return relative_path

            print(f"File {relative_path} already exists, keeping both versions")
            return relative_path.with_name(
                f"{relative_path.stem} ({self.name}){relative_path.suffix}"
            )

        return {
            rename_if_exists(relative_path): content
            for relative_path, content in self.project_file_contents(
                project, paths_to_update
            ).items()
        }

    def files_to_update(self, project, paths_to_update):
        return {
            relative_path: content
            for relative_path, content in self.project_file_contents(
                project, paths_to_update
            ).items()
            if str(relative_path) in paths_to_update
        }

    def create_files(self, project, paths_to_update=[]):
        return self.write_files(project, self.files_to_create(project, paths_to_update))

    def update_files(self, project, paths_to_update=[]):
        return self.write_files(project, self.files_to_update(project, paths_to_update))

    @hook("after_install")
    async def after_install(
        self,
        installer: PluginInstallService,
        plugin: ProjectPlugin,
        reason: PluginInstallReason,
    ):
        """Trigger after install tasks."""
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
            print(f"Adding '{plugin.name}' files to project...")

            for path in self.create_files(project, paths_to_update):
                print(f"Created {path}")
        elif reason is PluginInstallReason.UPGRADE:
            print(f"Updating '{plugin.name}' files in project...")

            updated_paths = self.update_files(project, paths_to_update)
            if not updated_paths:
                print("Nothing to update")
                return

            for path in updated_paths:
                print(f"Updated {path}")
        else:
            print(
                f"Run `meltano upgrade files` to update your project's '{plugin.name}' files."
            )
