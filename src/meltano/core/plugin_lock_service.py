"""Plugin Lockfile Service."""

from __future__ import annotations

import json
import typing as t
from hashlib import sha256

from structlog.stdlib import get_logger

from meltano.core.plugin.base import StandalonePlugin

if t.TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from meltano.core.plugin.base import PluginDefinition, PluginRef, Variant
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

    def __init__(
        self,
        project: Project,
        *,
        plugin_definition: PluginDefinition,
        variant_name: str | None = None,
    ) -> None:
        """Create a new PluginLock.

        Args:
            project: The project.
            plugin_definition: The plugin definition to lock.
            variant_name: The variant name to lock.
        """
        self.project = project
        self.definition = plugin_definition
        self.variant = self.definition.find_variant(variant_name)

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
            lockfile.write("\n")

    def load(
        self,
        *,
        create: bool = False,
        loader: Callable = lambda x: StandalonePlugin(**json.load(x)),
    ) -> StandalonePlugin:
        """Load the plugin lockfile.

        Args:
            create: Create the lockfile if it does not yet exist.
            loader: Function to process the lock file. Defaults to constructing
                a `StandalonePlugin` instance.

        Raises:
            FileNotFoundError: The lock file was not found at its expected path.

        Returns:
            The loaded plugin.
        """

        def _load():  # noqa: ANN202
            with self.path.open() as lockfile:
                return loader(lockfile)

        try:
            return _load()
        except FileNotFoundError:
            if create:
                self.save()
                return _load()
            raise

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

    def save_definition(
        self,
        *,
        path: Path,
        variant: Variant,
        definition: PluginDefinition,
    ) -> None:
        """Save the plugin lockfile."""
        locked_def = StandalonePlugin.from_variant(variant, definition)

        with path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)
            lockfile.write("\n")

    def save(
        self,
        plugin: ProjectPlugin,
        *,
        exists_ok: bool = False,
        fetch_from_hub: bool = False,
    ) -> None:
        """Save the plugin lockfile.

        Args:
            plugin: The plugin definition to save.
            exists_ok: Whether raise an exception if the lockfile already exists.
            fetch_from_hub: Whether to fetch the plugin definition from the Hub.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        if fetch_from_hub:
            definition = self.project.hub_service.find_definition(
                plugin.type,
                plugin.inherit_from or plugin.name,
                plugin.variant,
            )
        else:
            definition = plugin.definition

        variant = definition.find_variant(plugin.variant)
        path = self.project.plugin_lock_path(
            definition.type,
            definition.name,
            variant_name=variant.name,
        )

        if path.exists() and not exists_ok:
            msg = f"Lockfile already exists: {path}"
            raise LockfileAlreadyExistsError(msg, path, plugin)

        self.save_definition(
            path=path,
            variant=variant,
            definition=definition,
        )

        logger.debug("Locked plugin definition", path=path)
