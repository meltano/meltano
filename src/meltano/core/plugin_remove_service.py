"""Defines PluginRemoveService."""
import shutil

from meltano.core.plugin.project_plugin import ProjectPlugin

from .project import Project


class PluginRemoveService:
    """Handles plugin installation removal operations."""

    def __init__(self, project: Project):
        """Construct a PluginRemoveService instance."""
        self.project = project

    def remove_plugin(
        self,
        plugin: ProjectPlugin,
    ):
        """Remove a plugin installation."""
        path = self.project.meltano_dir().joinpath(plugin.type, plugin.name)

        remove = path.exists()
        if remove:
            shutil.rmtree(path)

        return remove
