"""Meltano Project Directories Service."""

from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, dataclass

import platformdirs

from meltano.core.utils import makedirs, sanitize_filename

if t.TYPE_CHECKING:
    from pathlib import Path

    from meltano.core._types import StrPath
    from meltano.core.plugin.base import PluginRef
    from meltano.core.project import Project


@dataclass
class ProjectDirsService:
    """Service for managing Meltano project directories and paths."""

    _: KW_ONLY

    root: Path
    """The root directory of the project."""

    sys_dir: Path
    """The system directory root of the project."""

    @classmethod
    def from_project(cls, project: Project) -> ProjectDirsService:
        """Create a ProjectDirsService from a Project."""
        return cls(root=project.root, sys_dir=project.sys_dir_root)

    def root_dir(self, *joinpaths: StrPath) -> Path:
        """Return the root directory of this project, optionally joined with path.

        Args:
            joinpaths: list of subdirs and/or file to join to project root.

        Returns:
            project root joined with provided subdirs and/or file
        """
        return self.root.joinpath(*joinpaths)

    @makedirs
    def meltano(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:  # noqa: ARG002
        """Path to the project `.meltano` directory.

        Args:
            joinpaths: Paths to join to the `.meltano` directory.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `.meltano` dir optionally joined to given paths.
        """
        return self.sys_dir.joinpath(*joinpaths)

    @makedirs
    def venvs(self, *prefixes: StrPath, make_dirs: bool = True) -> Path:
        """Path to a `venv` directory in `.meltano`.

        Args:
            prefixes: Paths to prepend to the `venv` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `venv` dir optionally prepended with given prefixes.
        """
        return self.meltano(*prefixes, "venv", make_dirs=make_dirs)

    @makedirs
    def run(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:
        """Path to the `run` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `run` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `run` dir optionally joined to given paths.
        """
        return self.meltano("run", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def logs(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:  # noqa: ARG002
        """Path to the `logs` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `logs` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `logs` dir optionally joined to given paths.
        """
        logs_path = platformdirs.user_log_path("meltano")
        return logs_path.joinpath(*joinpaths)

    @makedirs
    def job(
        self,
        state_id: str,
        *joinpaths: StrPath,
        make_dirs: bool = True,
    ) -> Path:
        """Path to the `elt` directory in `.meltano/run`.

        Args:
            state_id: State ID of `run` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.run(
            "elt",
            sanitize_filename(state_id),
            *joinpaths,
            make_dirs=make_dirs,
        )

    @makedirs
    def job_logs(
        self,
        state_id: str,
        *joinpaths: StrPath,
        make_dirs: bool = True,
    ) -> Path:
        """Path to the `elt` directory in `.meltano/logs`.

        Args:
            state_id: State ID of `logs` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano/logs`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.logs(
            "elt",
            sanitize_filename(state_id),
            *joinpaths,
            make_dirs=make_dirs,
        )

    @makedirs
    def plugin(
        self,
        plugin: PluginRef,
        *joinpaths: StrPath,
        make_dirs: bool = True,
    ) -> Path:
        """Path to the plugin installation directory in `.meltano`.

        Args:
            plugin: Plugin to retrieve or create directory for.
            joinpaths: Paths to join to the plugin installation directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to plugin installation dir optionally joined to given paths.
        """
        return self.meltano(
            plugin.type,
            plugin.plugin_dir_name,
            *joinpaths,
            make_dirs=make_dirs,
        )

    @makedirs
    def root_plugins(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:  # noqa: ARG002
        """Path to the project `plugins` directory.

        Args:
            joinpaths: Paths to join with the project `plugins` directory.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Path to the project `plugins` directory.
        """
        return self.root_dir("plugins", *joinpaths)

    @makedirs
    def plugin_lock_path(
        self,
        plugin_type: str,
        plugin_name: str,
        *,
        variant_name: str | None = None,
        make_dirs: bool = True,
    ) -> Path:
        """Path to the project lock file.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Path to the plugin lock file.
        """
        filename = f"{plugin_name}"

        if variant_name:
            filename = f"{filename}--{variant_name}"

        return self.root_plugins(
            plugin_type,
            f"{filename}.lock",
            make_dirs=make_dirs,
        )
