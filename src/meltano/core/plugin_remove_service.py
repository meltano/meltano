"""Defines PluginRemoveService."""
import shutil
from typing import Iterable

from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import ProjectPluginsService

from .project import Project


class PluginRemoveService:
    """Handles plugin installation removal operations."""

    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        """Construct a PluginRemoveService instance."""
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def remove_plugins(
        self,
        plugins: Iterable[ProjectPlugin],
    ):
        """Remove plugins."""
        plugin_removal_status = []

        for plugin in plugins:
            status = self.remove_plugin(plugin)
            plugin_removal_status.append(status)

        return plugin_removal_status

    def remove_plugin(self, plugin: ProjectPlugin):
        """Remove a plugin."""
        status = {
            "plugin_name": plugin.name,
            "removed_yaml": False,
            "removed_installation": False,
        }

        try:
            status["removed_yaml"] = bool(self.plugins_service.remove_from_file(plugin))
        except PluginNotFoundError:
            status["removed_yaml"] = False

        path = self.project.meltano_dir().joinpath(plugin.type, plugin.name)

        if path.exists():
            shutil.rmtree(path)
            status["removed_installation"] = True

        return status
