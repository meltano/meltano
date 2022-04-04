"""Plugin Lockfile Service."""

import yaml

from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project


class PluginLockfileService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
        """
        self.projet = project

    def save(self, project_plugin: ProjectPlugin):
        """Save the plugin lockfile.

        Args:
            project_plugin: The plugin definition to save.
        """
        with self.projet.plugin_lock_path(project_plugin).open("w") as lockfile:
            yaml.dump(project_plugin, lockfile)
