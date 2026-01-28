"""Add plugins to the project."""

from __future__ import annotations

import enum
import sys
import typing as t

import structlog

from meltano.core.plugin import BasePlugin, Variant
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.utils.python_compatibility import determine_plugin_python_version

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

if t.TYPE_CHECKING:
    from meltano.core.plugin import PluginType
    from meltano.core.project import Project
    from meltano.core.project_plugins_service import AddedPluginFlags

logger = structlog.stdlib.get_logger(__name__)


class PluginAddedReason(StrEnum):
    """The reason why a plugin was added to the project."""

    #: The plugin was added by the user.
    USER_REQUEST = enum.auto()

    #: The plugin was added because it is related to another plugin.
    RELATED = enum.auto()

    #: The plugin was added because it is required by another plugin.
    REQUIRED = enum.auto()


class MissingPluginException(Exception):
    """Raised when a plugin is not found."""


class ProjectAddService:
    """Project Add Service."""

    def __init__(self, project: Project):
        """Create a new Project Add Service.

        Args:
            project: The project to add plugins to.
        """
        self.project = project

    def add_with_flags(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        *,
        update: bool = False,
        **attrs: t.Any,
    ) -> tuple[ProjectPlugin, AddedPluginFlags]:
        """Add a new plugin to the project.

        Args:
            plugin_type: The type of the plugin to add.
            plugin_name: The name of the plugin to add.
            update: Whether to update the plugin.
            attrs: Additional attributes to add to the plugin.

        Returns:
            The added plugin and flags.
        """
        plugin = ProjectPlugin(
            plugin_type,
            plugin_name,
            **attrs,
            default_variant=Variant.DEFAULT_NAME,
        )
        self.project.plugins.ensure_parent(plugin)

        # If we are inheriting from a base plugin definition,
        # repeat the variant and pip_url in meltano.yml
        parent = plugin.parent
        if isinstance(parent, BasePlugin):
            plugin.variant = parent.variant
            plugin.pip_url = parent.pip_url

            # Auto-configure Python version if current version is not supported
            # Only auto-set if user didn't explicitly provide --python flag
            if (
                (attrs.get("python") is None)  # User didn't explicitly provide --python
                and (python_version := determine_plugin_python_version(parent._variant))
            ):
                plugin.python = python_version
                logger.warning(
                    "The current Python version is not supported by this plugin. "
                    "Automatically configured to use %s instead.",
                    python_version,
                    name=plugin.name,
                )

        plugin, flags = self.project.plugins.add_to_file_with_flags(
            plugin,
            update=update,
        )

        if not plugin.is_custom():
            self.project.plugins.lock_service.save(plugin, exists_ok=True)

        return plugin, flags

    def add(
        self,
        plugin_type: PluginType,
        plugin_name: str,
        *,
        update: bool = False,
        **attrs: t.Any,
    ) -> ProjectPlugin:
        """Add a plugin to the project.

        Args:
            plugin_type: The type of the plugin to add.
            plugin_name: The name of the plugin to add.
            lock: Whether to generate a lockfile for the plugin.
            update: Whether to update the plugin.
            attrs: Additional attributes to add to the plugin.

        Returns:
            The added plugin.
        """
        plugin, _flags = self.add_with_flags(
            plugin_type,
            plugin_name,
            update=update,
            **attrs,
        )
        return plugin

    def add_required(
        self,
        plugin: ProjectPlugin,
        *,
        lock: bool = True,
    ) -> list[ProjectPlugin]:
        """Add all required plugins to the project.

        Args:
            plugin: The plugin to get requirements from.
            lock: Whether to generate a lockfile for the plugin.

        Returns:
            The added plugins.
        """
        added_plugins: list[ProjectPlugin] = []
        for plugin_type, plugins in plugin.all_requires.items():
            for plugin_req in plugins:
                try:
                    plugin = self.add(
                        plugin_type,
                        plugin_req.name,
                        variant=plugin_req.variant,
                        lock=lock,
                    )
                except PluginAlreadyAddedException:
                    continue

                added_plugins.append(plugin)

        added_plugins_with_required: list[ProjectPlugin] = []
        for added in added_plugins:
            added_plugins_with_required.extend([added, *self.add_required(added)])

        return added_plugins_with_required
