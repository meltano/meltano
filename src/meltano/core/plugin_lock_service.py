"""Plugin Lockfile Service."""

from __future__ import annotations

import json
import typing as t
from dataclasses import dataclass
from functools import partial

from structlog.stdlib import get_logger

from meltano.core.cloud.config import CLOUD_API_ROOT
from meltano.core.error import MeltanoError
from meltano.core.hub.client import MeltanoHubService
from meltano.core.plugin.base import PluginDefinition, StandalonePlugin
from meltano.core.plugin.error import PluginNotFoundError

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core.plugin.base import PluginType
    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

logger = get_logger(__name__)

# The properties that change how a plugin runs. These are the ones that Meltano
# Cloud compares to offer an update, so that both report the same plugins. A
# change to presentation, such as a label or a description, is not an update.
UPDATE_PROPERTIES = (
    "namespace",
    "pip_url",
    "executable",
    "python",
    "capabilities",
    "select",
    "update",
    "metadata",
    "commands",
    "requires",
    "settings",
)
SETTING_UPDATE_PROPERTIES = (
    "name",
    "aliases",
    "value",
    "kind",
    "env",
    "options",
    "value_processor",
    "value_post_processor",
    "sensitive",
)


def _sort_lists(value: t.Any) -> t.Any:  # noqa: ANN401
    """Sort every list in a value, at any depth.

    No list in a definition has an order that changes how the plugin runs. The
    settings and their options are in the order that a form shows them, and the
    other lists are sets.

    Args:
        value: The value to sort.

    Returns:
        The value, with every list sorted.
    """
    if isinstance(value, dict):
        return {key: _sort_lists(item) for key, item in value.items()}
    if isinstance(value, list):
        return sorted(map(_sort_lists, value), key=partial(json.dumps, sort_keys=True))
    return value


def _runtime_definition(data: dict[str, t.Any]) -> dict[str, t.Any]:
    """Reduce a lock file to the properties that change how the plugin runs.

    An option contributes only its value, because its label is presentation.

    Args:
        data: The content of a lock file.

    Returns:
        The reduced definition.
    """
    settings = [
        {
            **{key: setting.get(key) for key in SETTING_UPDATE_PROPERTIES},
            "options": [option["value"] for option in setting.get("options") or []],
        }
        for setting in data.get("settings") or []
    ]
    return _sort_lists(
        {**{key: data.get(key) for key in UPDATE_PROPERTIES}, "settings": settings},
    )


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


@dataclass(frozen=True)
class PluginUpdate:
    """How the definition that Meltano Cloud serves differs from the lock file."""

    changes: tuple[str, ...]
    locked_pip_url: str | None
    served_pip_url: str | None

    @property
    def available(self) -> bool:
        """Whether the served definition runs differently from the lock file."""
        return bool(self.changes)


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

    def check_update(self, plugin: ProjectPlugin) -> PluginUpdate | None:
        """Compare the lock file with the definition that Meltano Cloud serves.

        The definition is reused from the Hub cache while it is fresh, so a
        check costs a request only once in each `INDEX_CACHE_DURATION`.

        Args:
            plugin: The plugin to check.

        Returns:
            How the served definition differs, or `None` if the plugin was not
            checked.
        """
        # The login is checked first, because building the Hub service for a
        # user who is logged out prints the login hint.
        if (
            plugin.is_custom()
            or plugin.inherit_from
            or not MeltanoHubService.cloud_credentials()
            or self.project.hub_service.hub_api_url != CLOUD_API_ROOT
        ):
            return None

        # The check only advises, so a Hub that cannot be reached, or that does
        # not serve the plugin, must not stop the plugin being listed or run.
        try:
            definition = self.project.hub_service.find_definition(
                plugin.type,
                plugin.name,
                variant_name=plugin.variant,
                refresh=False,
            )
        except (PluginNotFoundError, MeltanoError) as err:
            logger.debug(
                "Unable to check for a plugin update",
                plugin=plugin.name,
                error=str(err),
            )
            return None

        served = StandalonePlugin.from_variant(
            definition.find_variant(plugin.variant),
            definition,
        )
        # Written and read back as JSON, the same as a lock file.
        served_data = json.loads(json.dumps(served.canonical()))
        locked_data = self.get_standalone_data(plugin)
        served_runtime = _runtime_definition(served_data)
        locked_runtime = _runtime_definition(locked_data)
        return PluginUpdate(
            changes=tuple(
                key
                for key in UPDATE_PROPERTIES
                if served_runtime[key] != locked_runtime[key]
            ),
            locked_pip_url=locked_data.get("pip_url"),
            served_pip_url=served_data.get("pip_url"),
        )
