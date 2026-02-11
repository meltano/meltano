"""Plugin Lockfile Service."""

from __future__ import annotations

import json
import typing as t
from dataclasses import dataclass

from structlog.stdlib import get_logger

from meltano.core.plugin.base import PluginDefinition, StandalonePlugin

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.plugin.base import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

logger = get_logger(__name__)


class LockfileAlreadyExistsError(Exception):
    """Raised when a plugin lockfile already exists."""

    def __init__(self, message: str, path: Path):
        """Create a new LockfileAlreadyExistsError.

        Args:
            message: The error message.
            path: The path to the existing lockfile.
            plugin: The plugin that was locked.
        """
        self.path = path
        super().__init__(message)


@dataclass
class VariantMetadata:
    """Metadata for a variant."""

    is_default: bool | None = None
    is_deprecated: bool | None = None


class PluginLockService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
        """
        self.project = project

    def lock_path(
        self,
        *,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> Path:
        """Get the path to the plugin lockfile from a type, name, and variant."""
        return self.project.dirs.plugin_lock_path(
            plugin_type,
            plugin_name,
            variant_name=variant_name,
        )

    def plugin_lock_path(
        self,
        *,
        plugin: ProjectPlugin,
        variant_name: str | None = None,
    ) -> Path:
        """Get the path to the plugin lockfile from a plugin and variant."""
        return self.lock_path(
            plugin_type=plugin.type,
            plugin_name=plugin.inherit_from or plugin.name,
            variant_name=variant_name,
        )

    def save_definition(
        self,
        *,
        definition: PluginDefinition,
        variant_name: str | None = None,
        exists_ok: bool = False,
    ) -> Path:
        """Save the plugin lockfile.

        Args:
            definition: The plugin definition to save.
            variant_name: The variant name to save.
            exists_ok: Whether to raise an exception if the lockfile already exists.

        Returns:
            The path to the plugin lockfile.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        variant = definition.find_variant(variant_name)
        path = self.lock_path(
            plugin_type=definition.type,
            plugin_name=definition.name,
            variant_name=variant.name,
        )

        if path.exists() and not exists_ok:
            msg = f"Lockfile already exists: {path}"
            raise LockfileAlreadyExistsError(msg, path)

        locked_def = StandalonePlugin.from_variant(variant, definition)

        with path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)
            lockfile.write("\n")

        logger.debug("Locked plugin definition", path=path)
        return path

    def _save_from_hub(
        self,
        *,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
        exists_ok: bool = False,
    ) -> tuple[Path, VariantMetadata]:
        """Save the plugin lockfile."""
        definition = self.project.hub_service.find_definition(
            plugin_type,
            plugin_name,
            variant_name=variant_name,
        )
        variant_metadata = VariantMetadata(
            is_default=definition.is_default_variant,
            is_deprecated=definition.find_variant(variant_name).deprecated,
        )
        path = self.save_definition(
            variant_name=variant_name,
            definition=definition,
            exists_ok=exists_ok,
        )
        return path, variant_metadata

    def _save_from_project_plugin(
        self,
        *,
        plugin: ProjectPlugin,
        exists_ok: bool = False,
    ) -> Path:
        """Save the plugin lockfile."""
        return self.save_definition(
            variant_name=plugin.variant,
            definition=plugin.definition,
            exists_ok=exists_ok,
        )

    def save(
        self,
        plugin: ProjectPlugin,
        *,
        exists_ok: bool = False,
        fetch_from_hub: bool = False,
    ) -> Path:
        """Save the plugin lockfile.

        Args:
            plugin: The plugin definition to save.
            exists_ok: Whether raise an exception if the lockfile already exists.
            fetch_from_hub: Whether to fetch the plugin definition from the Hub.

        Returns:
            The path to the plugin lockfile.

        """
        if fetch_from_hub:
            path, _ = self._save_from_hub(
                plugin_type=plugin.type,
                plugin_name=plugin.inherit_from or plugin.name,
                variant_name=plugin.variant,
                exists_ok=exists_ok,
            )
            return path

        return self._save_from_project_plugin(plugin=plugin, exists_ok=exists_ok)

    def load_content(
        self,
        *,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> tuple[dict[str, t.Any], VariantMetadata]:
        """Load the content of the plugin lockfile."""
        variant_metadata = VariantMetadata()
        path = self.lock_path(
            plugin_type=plugin_type,
            plugin_name=plugin_name,
            variant_name=variant_name,
        )
        if not path.exists():
            path, variant_metadata = self._save_from_hub(
                plugin_type=plugin_type,
                plugin_name=plugin_name,
                variant_name=variant_name,
                exists_ok=True,
            )

        with path.open() as lockfile:
            return json.load(lockfile), variant_metadata

    def get_standalone_data(self, plugin: ProjectPlugin) -> dict[str, t.Any]:
        """Get the standalone data for a plugin."""
        path = self.lock_path(
            plugin_type=plugin.type,
            plugin_name=plugin.inherit_from or plugin.name,
            variant_name=plugin.variant,
        )
        if path.exists():
            with path.open() as lockfile:
                return json.load(lockfile)

        return StandalonePlugin.from_variant(
            plugin.definition.find_variant(None),
            plugin.definition,
        ).canonical()

    def load_definition(
        self,
        *,
        plugin_type: PluginType,
        plugin_name: str,
        variant_name: str | None = None,
    ) -> PluginDefinition:
        """Load the plugin definition from the lockfile."""
        content, variant_metadata = self.load_content(
            plugin_type=plugin_type,
            plugin_name=plugin_name,
            variant_name=variant_name,
        )
        return PluginDefinition.from_standalone(
            StandalonePlugin.parse(content),
            is_default_variant=variant_metadata.is_default,
            deprecated=variant_metadata.is_deprecated,
        )
