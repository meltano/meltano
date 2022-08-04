"""Plugin Lockfile Service."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from structlog.stdlib import get_logger

from meltano.core.plugin.base import PluginRef, StandalonePlugin
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


class PluginLock:
    """Plugin lockfile."""

    def __init__(self, project: Project, plugin: ProjectPlugin) -> None:
        """Create a new PluginLock.

        Args:
            project: The project.
            plugin: The plugin to lock.
        """
        self.project = project
        self.definition = plugin.definition
        self.variant = self.definition.find_variant(plugin.variant)

        self.path = self.project.plugin_lock_path(
            self.definition.type,
            self.definition.name,
            variant_name=self.variant.name,
        )

    def save(self) -> None:
        """Save the plugin lockfile."""
        locked_def = StandalonePlugin.from_variant(self.variant, self.definition)

        with self.path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)

    def load(self) -> StandalonePlugin:
        """Load the plugin lockfile.

        Returns:
            The loaded plugin.
        """
        with self.path.open() as lockfile:
            locked_def = json.load(lockfile)

        return StandalonePlugin(**locked_def)

    @property
    def sha256_checksum(self) -> str:
        """Get the checksum of the lockfile.

        Returns:
            The checksum of the lockfile.
        """
        return sha256(self.path.read_bytes()).hexdigest()


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
        exists_ok: bool = False,
    ):
        """Save the plugin lockfile.

        Args:
            plugin: The plugin definition to save.
            exists_ok: Whether raise an exception if the lockfile already exists.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        plugin_lock = PluginLock(self.project, plugin)

        if plugin_lock.path.exists() and not exists_ok:
            raise LockfileAlreadyExistsError(
                f"Lockfile already exists: {plugin_lock.path}",
                plugin_lock.path,
                plugin,
            )

        plugin_lock.save()

        logger.debug("Locked plugin definition", path=plugin_lock.path)
