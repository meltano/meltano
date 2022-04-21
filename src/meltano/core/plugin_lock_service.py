"""Plugin Lockfile Service."""

from __future__ import annotations

import json

from meltano.core.plugin.base import BasePlugin, StandalonePlugin, Variant
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.project import Project


class LockfileAlreadyExistsError(Exception):
    """Raised when a plugin lockfile already exists."""


class PluginLockService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project, discovery_service: PluginDiscoveryService):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
            discovery_service: The plugin discovery service.
        """
        self.projet = project
        self.discovery_service = discovery_service

    def save(
        self,
        project_plugin: ProjectPlugin | BasePlugin,
        *,
        overwrite: bool = False,
    ):
        """Save the plugin lockfile.

        Args:
            project_plugin: The plugin definition to save.
            overwrite: Whether to overwrite the lockfile if it already exists.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        variant = (
            None
            if project_plugin.variant == Variant.DEFAULT_NAME
            else project_plugin.variant
        )

        if isinstance(project_plugin, BasePlugin):
            plugin_def = project_plugin.definition
            path = self.projet.plugin_lock_path(
                plugin_def.type,
                plugin_def.name,
                variant_name=variant,
            )

        elif project_plugin.inherit_from is None:
            path = self.projet.plugin_lock_path(
                project_plugin.type,
                project_plugin.name,
                variant_name=variant,
            )
            plugin_def = self.discovery_service.find_definition(
                project_plugin.type,
                project_plugin.name,
            )
        else:
            self.save(project_plugin.parent, overwrite=overwrite)
            return

        if path.exists() and not overwrite:
            raise LockfileAlreadyExistsError(f"Lockfile already exists: {path}")

        variant = plugin_def.find_variant(project_plugin.variant)
        locked_def = StandalonePlugin.from_variant(
            variant,
            project_plugin.name,
            project_plugin.namespace,
            project_plugin.type,
        )

        with path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)
