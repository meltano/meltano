"""Defines PluginLocationRemoveStatus, PluginLocationRemoveManager, DbRemoveManager, MeltanoYmlRemoveManager and InstallationRemoveManager."""

import shutil
from abc import ABC, abstractmethod
from enum import Enum

import sqlalchemy
from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project
from .settings_store import SettingValueStore


class PluginLocationRemoveStatus(Enum):
    """Possible remove statuses."""

    REMOVED = "removed"
    ERROR = "error"
    NOT_FOUND = "not found"


class PluginLocationRemoveManager(ABC):
    """Handle removal of a plugin from a given location."""

    def __init__(self, plugin: ProjectPlugin, location):
        """Construct a PluginLocationRemoveManager instance."""
        self.plugin = plugin
        self.plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"
        self.location = location
        self.remove_status = None
        self.remove_message = None

    @abstractmethod
    def remove(self):
        """Abstract remove method."""
        pass

    @property
    def plugin_removed(self) -> bool:
        """Wether or not the plugin was successfully removed."""
        return self.remove_status is PluginLocationRemoveStatus.REMOVED

    @property
    def plugin_not_found(self) -> bool:
        """Wether or not the plugin was not found to remove."""
        return self.remove_status is PluginLocationRemoveStatus.NOT_FOUND

    @property
    def plugin_error(self) -> bool:
        """Wether or not an error was encountered the plugin removal process."""
        return self.remove_status is PluginLocationRemoveStatus.ERROR


class DbRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin's settings from the system database `plugin_settings` table."""

    def __init__(self, plugin, project):
        """Construct a DbRemoveManager instance."""
        super().__init__(plugin, "system database")
        self.plugins_settings_service = PluginSettingsService(project, plugin)
        self.session = project_engine(project)[1]

    def remove(self):
        """Remove the plugin's settings from the system database `plugin_settings` table."""
        session = self.session()
        try:
            self.plugins_settings_service.reset(
                store=SettingValueStore.DB, session=session
            )
        except sqlalchemy.exc.OperationalError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = err.orig
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED


class MeltanoYmlRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin from `meltano.yml`."""

    def __init__(self, plugin, project: Project):
        """Construct a MeltanoYmlRemoveManager instance."""
        super().__init__(plugin, str(project.meltanofile.relative_to(project.root)))
        self.project_plugins_service = ProjectPluginsService(project)

    def remove(self):
        """Remove the plugin from `meltano.yml`."""
        try:
            self.project_plugins_service.remove_from_file(self.plugin)
        except PluginNotFoundError:
            self.remove_status = PluginLocationRemoveStatus.NOT_FOUND
            return
        except OSError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = err.strerror
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED


class InstallationRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin installation from `.meltano`."""

    def __init__(self, plugin, project: Project):
        """Construct a InstallationRemoveManager instance."""
        path = project.plugin_dir(plugin, make_dirs=False)
        super().__init__(plugin, str(path.parent.relative_to(project.root)))
        self.path = path

    def remove(self):
        """Remove the plugin installation from `.meltano`."""
        if not self.path.exists():
            self.remove_status = PluginLocationRemoveStatus.NOT_FOUND
            self.message = f"{self.plugin_descriptor} not found in {self.path.parent}"
            return

        try:
            shutil.rmtree(self.path)
        except OSError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = err.strerror
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED
