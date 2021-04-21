"""Defines PluginRemoveService."""
import shutil
from typing import Iterable

from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project
from .settings_store import SettingValueStore
from .utils import noop


class PluginRemoveService:
    """Handle plugin installation removal operations."""

    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        """Construct a PluginRemoveService instance."""
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def remove_plugins(self, plugins: Iterable[ProjectPlugin], status_cb=noop):
        """Remove multiple plugins."""
        num_plugins: int = len(plugins)
        removed_plugins: int = num_plugins

        for plugin in plugins:
            status = "running"
            message = ""
            status_cb(plugin, status)

            meltano_yml, installation = self.remove_plugin(plugin)

            if meltano_yml.removed and installation.removed:
                status = "success"
            elif installation.removed:
                status = "partial_success"
                message = meltano_yml.message
            elif meltano_yml.removed:
                status = "partial_success"
                message = installation.message
            else:
                status = "nothing_to_remove"
                removed_plugins -= 1

            status_cb(plugin, status, message)

        return removed_plugins, num_plugins

    def remove_plugin(self, plugin: ProjectPlugin):
        """Remove a plugin from `meltano.yml` and its installation in `.meltano`."""

        meltano_yml_remove_status = RemoveStatus("meltano.yml")
        installation_remove_status = RemoveStatus("installation")

        plugins_settings_service = PluginSettingsService(self.project, plugin)

        _, session = project_engine(self.project)
        plugins_settings_service.reset(store=SettingValueStore.DB, session=session())

        try:
            meltano_yml_remove_status.removed = bool(
                self.plugins_service.remove_from_file(plugin)
            )
        except PluginNotFoundError:
            meltano_yml_remove_status.message = (
                f"no such {plugin.type.descriptor} in meltano.yml to remove"
            )

        path = self.project.meltano_dir().joinpath(plugin.type, plugin.name)

        if path.exists():
            shutil.rmtree(path)
            installation_remove_status.removed = True
        else:
            installation_remove_status.message = (
                f"no install in .meltano/{plugin.type} to remove"
            )

        return meltano_yml_remove_status, installation_remove_status


class RemoveStatus:
    """Handle plugin removal status for a single location."""

    def __init__(
        self,
        location,
        removed=False,
        message="",
    ):
        """Construct a RemoveStatus instance."""
        self.location = location
        self.removed = removed
        self.message = message
