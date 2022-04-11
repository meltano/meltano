"""Plugin Lockfile Service."""

from __future__ import annotations

import json

from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin.base import Variant
from meltano.core.plugin.command import Command
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.project import Project
from meltano.core.setting_definition import SettingDefinition


class LockfileAlreadyExistsError(Exception):
    """Raised when a plugin lockfile already exists."""


class LockedPlugin(Canonical):
    """A plugin that is locked to a specific definition."""

    def __init__(
        self,
        name: str = None,
        namespace: str = None,
        docs: str | None = None,
        repo: str | None = None,
        pip_url: str | None = None,
        executable: str | None = None,
        capabilities: list | None = None,
        settings_group_validation: list | None = None,
        settings: list | None = None,
        commands: dict | None = None,
        **extras,
    ):
        """Create a locked plugin.

        Args:
            name: The name of the plugin.
            namespace: The namespace of the plugin.
            docs: The documentation URL of the plugin.
            repo: The repository URL of the plugin.
            pip_url: The pip URL of the plugin.
            executable: The executable of the plugin.
            capabilities: The capabilities of the plugin.
            settings_group_validation: The settings group validation of the plugin.
            settings: The settings of the plugin.
            commands: The commands of the plugin.
            extras: Additional attributes to set on the plugin.
        """
        super().__init__(
            name=name,
            namespace=namespace,
            docs=docs,
            repo=repo,
            pip_url=pip_url,
            executable=executable,
            capabilities=capabilities or [],
            settings_group_validation=settings_group_validation or [],
            settings=list(map(SettingDefinition.parse, settings or [])),
            commands=Command.parse_all(commands),
            extras=extras,
        )

    @classmethod
    def from_variant(cls, variant: Variant, name: str, namespace: str):
        """Create a locked plugin from a variant.

        Args:
            variant: The variant to create the plugin from.
            name: The name of the plugin.
            namespace: The namespace of the plugin.

        Returns:
            A locked plugin definition.
        """
        return cls(
            name=name,
            namespace=namespace,
            docs=variant.docs,
            repo=variant.repo,
            pip_url=variant.pip_url,
            executable=variant.executable,
            capabilities=variant.capabilities,
            settings_group_validation=variant.settings_group_validation,
            settings=variant.settings,
            commands=variant.commands,
            **variant.extras,
        )


class PluginLockfileService:
    """Plugin Lockfile Service."""

    def __init__(self, project: Project, discovery_service: PluginDiscoveryService):
        """Create a new Plugin Lockfile Service.

        Args:
            project: The Meltano project.
            discovery_service: The plugin discovery service.
        """
        self.projet = project
        self.discovery_service = discovery_service

    def save(self, project_plugin: ProjectPlugin, *, overwrite: bool = False):
        """Save the plugin lockfile.

        Args:
            project_plugin: The plugin definition to save.
            overwrite: Whether to overwrite the lockfile if it already exists.

        Raises:
            LockfileAlreadyExistsError: If the lockfile already exists and is not
                flagged for overwriting.
        """
        if not isinstance(project_plugin, ProjectPlugin):
            return

        if project_plugin.inherit_from is None:
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
        else:
            self.save(project_plugin.parent, overwrite=overwrite)
            return

        if path.exists() and not overwrite:
            raise LockfileAlreadyExistsError(f"Lockfile already exists: {path}")

        plugin_def = self.discovery_service.find_definition(
            project_plugin.type,
            project_plugin.name,
        )

        variant = plugin_def.find_variant(project_plugin.variant)
        locked_def = LockedPlugin.from_variant(
            variant,
            project_plugin.name,
            project_plugin.namespace,
        )

        with path.open("w") as lockfile:
            json.dump(locked_def.canonical(), lockfile, indent=2)
