"""Plugin Lockfile Service."""

import json

from meltano.core.plugin.base import Variant
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
        variant = (
            None
            if project_plugin.variant == Variant.DEFAULT_NAME
            else project_plugin.variant
        )
        path = self.projet.plugin_lock_path(
            project_plugin.type,
            project_plugin.name,
            variant_name=variant,
        )
        with path.open("w") as lockfile:
            json.dump(project_plugin.canonical(), lockfile, indent=2)
