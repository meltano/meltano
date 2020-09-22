import logging
from pathlib import Path

from meltano.core.db import project_engine
from meltano.core.plugin import ProjectPlugin, PluginType
from meltano.core.plugin_install_service import PluginInstallReason
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.behavior.hookable import hook
from meltano.core.venv_service import VirtualEnv
from meltano.core.setting_definition import SettingDefinition


class FilePlugin(ProjectPlugin):
    __plugin_type__ = PluginType.FILES

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__plugin_type__, *args, **kwargs)

        self._update_config = None

    @property
    def extra_settings(self):
        return [
            SettingDefinition(
                name="_update", kind="object", aliases=["update"], value={}
            )
        ]

    def is_invokable(self):
        return False

    def should_add_to_file(self, project):
        return len(self.update_config(project)) > 0

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

    def project_file_contents(self, project):
        def prepend_update_header(content, relative_path):
            if self.should_update_file(project, relative_path):
                content = "\n\n".join([self.update_file_header(relative_path), content])

            return content

        return {
            relative_path: prepend_update_header(content, relative_path)
            for relative_path, content in self.file_contents(project).items()
        }

    def update_config(self, project):
        if self._update_config is None:
            plugin_settings_service = PluginSettingsService(project, self)
            self._update_config = plugin_settings_service.get("_update")

        return self._update_config

    def should_update_file(self, project, relative_path):
        try:
            return self.update_config(project)[str(relative_path)]
        except KeyError:
            return False

    def file_exists(self, project, relative_path):
        return project.root_dir(relative_path).exists()

    def write_file(self, project, relative_path, content):
        project_path = project.root_dir(relative_path)
        if project_path.exists() and project_path.read_text() == content:
            return False

        project_path.parent.mkdir(parents=True, exist_ok=True)
        project_path.write_text(content)

        return True

    def write_files(self, project, files_content):
        paths = []
        for relative_path, content in files_content.items():
            if self.write_file(project, relative_path, content):
                paths.append(relative_path)

        return paths

    def files_to_create(self, project):
        def rename_if_exists(relative_path):
            exists = self.file_exists(project, relative_path)
            if not exists:
                return relative_path

            print(f"File {relative_path} already exists, keeping both versions")
            return relative_path.with_name(
                f"{relative_path.stem} ({self.name}){relative_path.suffix}"
            )

        return {
            rename_if_exists(relative_path): content
            for relative_path, content in self.project_file_contents(project).items()
        }

    def files_to_update(self, project):
        return {
            relative_path: content
            for relative_path, content in self.project_file_contents(project).items()
            if self.should_update_file(project, relative_path)
        }

    def create_files(self, project):
        return self.write_files(project, self.files_to_create(project))

    def update_files(self, project):
        return self.write_files(project, self.files_to_update(project))

    @hook("after_install")
    def after_install(self, project, reason):
        if reason is PluginInstallReason.ADD:
            print(f"Adding '{self.name}' files to project...")

            for path in self.create_files(project):
                print(f"Created {path}")
        elif reason is PluginInstallReason.UPGRADE:
            print(f"Updating '{self.name}' files in project...")

            updated_paths = self.update_files(project)
            if not updated_paths:
                print("Nothing to update")
                return

            for path in updated_paths:
                print(f"Updated {path}")
        else:
            print(
                f"Run `meltano upgrade files` to update your project's '{self.name}' files."
            )
