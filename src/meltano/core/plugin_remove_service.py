"""Defines PluginRemoveService."""
import shutil
from enum import Enum
from typing import Iterable

from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project
from .settings_store import SettingValueStore
from .utils import noop


class PluginRemoveStatus(Enum):
    """Possible remove statuses."""

    REMOVED = "removed"
    ERROR = "error"
    NOT_FOUND = "not found"
    RUNNING = "running"


class PluginRemoveState:
    """Handle plugin removal state for a single location."""

    def __init__(
        self,
        location,
        message="",
        status=PluginRemoveStatus.RUNNING,
    ):
        """Construct a RemoveState instance."""
        self.location = location
        self.message = message
        self.status = status


class PluginRemoveService:
    """Handle plugin installation removal operations."""

    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        """Construct a PluginRemoveService instance."""
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def remove_plugins(
        self, plugins: Iterable[ProjectPlugin], status_cb=noop
    ) -> tuple[int, int]:
        """
        Remove multiple plugins.

        Returns a tuple containing:
        1. The total number of removed plugins
        2. The total number of plugins attempted
        """
        num_plugins: int = len(plugins)
        removed_plugins: int = num_plugins

        for plugin in plugins:
            status_cb(plugin, PluginRemoveStatus.RUNNING)

            meltano_yml, installation = self.remove_plugin(plugin)

            if meltano_yml.status is not PluginRemoveStatus.REMOVED:
                if installation.status is not PluginRemoveStatus.REMOVED:
                    removed_plugins -= 1

            status_cb(plugin, meltano_yml)
            status_cb(plugin, installation)

        return removed_plugins, num_plugins

    def remove_plugin(
        self, plugin: ProjectPlugin
    ) -> tuple[PluginRemoveState, PluginRemoveState]:
        """
        Remove a plugin from `meltano.yml`, its installation in `.meltano`, and any settings in the Meltano system database.

        Returns a tuple containing:
        1. Removal state for `meltano.yml`
        2. Removal state for installation
        """
        yml_remove_state = PluginRemoveState("meltano.yml")
        installation_remove_state = PluginRemoveState(f".meltano/{plugin.type}")

        plugins_settings_service = PluginSettingsService(self.project, plugin)

        _, session = project_engine(self.project)
        plugins_settings_service.reset(store=SettingValueStore.DB, session=session())

        yml_remove_state.status = PluginRemoveStatus.REMOVED
        try:
            self.plugins_service.remove_from_file(plugin)
        except PluginNotFoundError:
            yml_remove_state.status = PluginRemoveStatus.NOT_FOUND

        path = self.project.meltano_dir().joinpath(plugin.type, plugin.name)

        if path.exists():
            installation_remove_state.status = PluginRemoveStatus.REMOVED
            try:
                shutil.rmtree(path)
            except OSError as err:
                installation_remove_state.status = PluginRemoveStatus.ERROR
                installation_remove_state.message = err.strerror
        else:
            installation_remove_state.status = PluginRemoveStatus.NOT_FOUND

        return yml_remove_state, installation_remove_state
