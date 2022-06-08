"""Plugin Lockfile Service."""

from __future__ import annotations

import json
from pathlib import Path

from structlog.stdlib import get_logger

from meltano.core.plugin.base import PluginRef, StandalonePlugin, Variant
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project import Project

logger = get_logger(__name__)


class LockfileAlreadyExistsError(Exception):
    """Raised when a plugin lockfile already exists."""

    def __init__(self, message: str, path: Path, plugin: PluginRef):
        """Create a new LockfileAlreadyExistsError.

        Args:
            message: The error message.
            path: The path to the existing lockfile.
            plugin: The plugin that was locked.
        """
        self.path = path
        self.plugin = plugin
        super().__init__(message)


class PluginLockService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
        """
        self.project = project

    def save(
        self,
        plugin: ProjectPlugin,
        *,
        overwrite: bool = False,
        exists_ok: bool = False,
    ):
        """Save the plugin lockfile.

        Args:
            plugin: The plugin definition to save.
            overwrite: Whether to overwrite the lockfile if it already exists.
            exists_ok: Whether raise an exception if the lockfile already exists.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        base_plugin = plugin.parent
        variant = (
            None if base_plugin.variant == Variant.DEFAULT_NAME else base_plugin.variant
        )

        plugin_def = base_plugin.definition
        path = self.project.plugin_lock_path(
            plugin_def.type,
            plugin_def.name,
            variant_name=variant,
        )

        if path.exists() and not overwrite and not exists_ok:
            raise LockfileAlreadyExistsError(
                f"Lockfile already exists: {path}",
                path,
                plugin,
            )

        variant = plugin_def.find_variant(base_plugin.variant)
        locked_def = StandalonePlugin.from_variant(
            variant,
            base_plugin.name,
            base_plugin.namespace,
            base_plugin.type,
            label=base_plugin.label,
        )

        with path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)

        logger.debug("Locked plugin definition", path=path)
