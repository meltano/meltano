"""Defines plugin removers."""

from __future__ import annotations

import shutil
import typing as t
from abc import ABC, abstractmethod
from enum import Enum

import sqlalchemy
import sqlalchemy.exc

from meltano.core.db import project_engine
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.settings_service import PluginSettingsService

from .settings_store import SettingValueStore

if t.TYPE_CHECKING:
    from meltano.core.plugin.project_plugin import ProjectPlugin

    from .project import Project


class PluginLocationRemoveStatus(Enum):
    """Possible remove statuses."""

    REMOVED = "removed"
    ERROR = "error"
    NOT_FOUND = "not found"


class PluginLocationRemoveManager(ABC):
    """Handle removal of a plugin from a given location."""

    def __init__(self, plugin: ProjectPlugin, location: str) -> None:
        """Construct a PluginLocationRemoveManager instance.

        Args:
            plugin: The plugin to remove.
            location: The location to remove the plugin from.
        """
        self.plugin = plugin
        self.plugin_descriptor = f"{plugin.type.descriptor} '{plugin.name}'"
        self.location = location
        self.remove_status: PluginLocationRemoveStatus | None = None
        self.message: str | None = None

    @abstractmethod
    def remove(self) -> None:
        """Abstract remove method."""

    @property
    def plugin_removed(self) -> bool:
        """Wether or not the plugin was successfully removed.

        Returns:
            True if the plugin was successfully removed, False otherwise.
        """
        return self.remove_status is PluginLocationRemoveStatus.REMOVED

    @property
    def plugin_not_found(self) -> bool:
        """Wether or not the plugin was not found to remove.

        Returns:
            True if the plugin was not found, False otherwise.
        """
        return self.remove_status is PluginLocationRemoveStatus.NOT_FOUND

    @property
    def plugin_error(self) -> bool:
        """Wether or not an error was encountered the plugin removal process.

        Returns:
            True if an error was encountered, False otherwise.
        """
        return self.remove_status is PluginLocationRemoveStatus.ERROR


class DbRemoveManager(PluginLocationRemoveManager):
    """Handle removal from the system db `plugin_settings` table."""

    def __init__(self, plugin: ProjectPlugin, project: Project) -> None:
        """Construct a DbRemoveManager instance.

        Args:
            plugin: The plugin to remove.
            project: The Meltano project.
        """
        super().__init__(plugin, "system database")
        self.plugins_settings_service = PluginSettingsService(project, plugin)
        self.session = project_engine(project)[1]

    def remove(self) -> None:
        """Remove the plugin's settings from the system db `plugin_settings` table.

        Returns:
            The remove status.
        """
        session = self.session()
        try:
            self.plugins_settings_service.reset(
                store=SettingValueStore.DB,
                session=session,
            )
        except sqlalchemy.exc.OperationalError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = str(err.orig) if err.orig else str(err)
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED


class MeltanoYmlRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin from `meltano.yml`."""

    def __init__(self, plugin: ProjectPlugin, project: Project) -> None:
        """Construct a MeltanoYmlRemoveManager instance.

        Args:
            plugin: The plugin to remove.
            project: The Meltano project.
        """
        super().__init__(plugin, str(project.meltanofile.relative_to(project.root)))
        self.project = project

    def remove(self) -> None:
        """Remove the plugin from `meltano.yml`."""
        try:
            self.project.plugins.remove_from_file(self.plugin)
        except PluginNotFoundError:
            self.remove_status = PluginLocationRemoveStatus.NOT_FOUND
            return
        except OSError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = err.strerror
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED


class LockedDefinitionRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin locked definition from `plugins/`."""

    def __init__(self, plugin: ProjectPlugin, project: Project) -> None:
        """Construct a LockedDefinitionRemoveManager instance.

        Args:
            plugin: The plugin to remove.
            project: The Meltano project.
        """
        lockfile_dir = project.root_plugins_dir(plugin.type)  # type: ignore[deprecated]
        glob_expr = f"{plugin.name}*.lock"
        super().__init__(
            plugin,
            str(lockfile_dir.relative_to(project.root).joinpath(glob_expr)),
        )

        self.paths = list(lockfile_dir.glob(glob_expr))

    def remove(self) -> None:
        """Remove the plugin from `plugins/`."""
        if not self.paths:
            self.remove_status = PluginLocationRemoveStatus.NOT_FOUND
            return

        try:
            for path in self.paths:
                path.unlink()
        except OSError as err:
            self.remove_status = PluginLocationRemoveStatus.ERROR
            self.message = err.strerror
            return

        self.remove_status = PluginLocationRemoveStatus.REMOVED


class InstallationRemoveManager(PluginLocationRemoveManager):
    """Handle removal of a plugin installation from `.meltano`."""

    def __init__(self, plugin: ProjectPlugin, project: Project) -> None:
        """Construct a InstallationRemoveManager instance.

        Args:
            plugin: The plugin to remove.
            project: The Meltano project.
        """
        path = project.plugin_dir(plugin, make_dirs=False)  # type: ignore[deprecated]
        super().__init__(plugin, str(path.parent.relative_to(project.root)))
        self.path = path

    def remove(self) -> None:
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
