"""Meltano Projects."""

from __future__ import annotations

import errno
import os
import sys
import threading
import typing as t
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path

import fasteners
import structlog
from dotenv import dotenv_values

from meltano.core import yaml
from meltano.core._compat import MeltanoInternalDeprecationWarning, deprecated
from meltano.core.config_service import ConfigService
from meltano.core.environment import Environment
from meltano.core.error import (
    EmptyMeltanoFileException,
    ProjectNotFound,
    ProjectReadonly,
)
from meltano.core.hub import MeltanoHubService
from meltano.core.project_dirs_service import ProjectDirsService
from meltano.core.project_files import ProjectFiles
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import (
    check_meltano_compatibility,
    get_meltano_version,
    makedirs,
    truthy,
)

if t.TYPE_CHECKING:
    from collections.abc import Generator

    from meltano.core._types import StrPath
    from meltano.core.meltano_file import MeltanoFile as MeltanoFileTypeHint
    from meltano.core.plugin.base import PluginRef


logger = structlog.stdlib.get_logger(__name__)


PROJECT_ROOT_ENV = "MELTANO_PROJECT_ROOT"
PROJECT_ENVIRONMENT_ENV = "MELTANO_ENVIRONMENT"
PROJECT_READONLY_ENV = "MELTANO_PROJECT_READONLY"
PROJECT_SYS_DIR_ROOT_ENV = "MELTANO_SYS_DIR_ROOT"
MELTANO_USER_AGENT_ENV = "MELTANO_USER_AGENT"


def walk_parent_directories() -> Generator[Path, None, None]:
    """Yield each directory starting with the current up to the root.

    Yields:
        parent directories
    """
    directory = Path.cwd()
    while True:
        yield directory

        parent_directory = directory.parent
        if parent_directory == directory:
            return
        directory = parent_directory


class Project:
    """Represents a Meltano project."""

    _activate_lock = threading.Lock()
    _find_lock = threading.Lock()
    _meltano_rw_lock = fasteners.ReaderWriterLock()
    _default: t.ClassVar[Project | None] = None

    def __init__(
        self,
        root: StrPath,
        environment: Environment | None = None,
        *,
        readonly: bool = False,
        dotenv_file: Path | None = None,
    ):
        """Initialize a `Project` instance.

        Args:
            root: The root directory of the project.
            environment: The active Meltano environment.
            readonly: Whether the project is in read-only mode.
            dotenv_file: The path to the .env file to use.
        """
        self.root = Path(root).resolve()
        self.environment: Environment | None = environment
        self.readonly = readonly
        self.sys_dir_root = Path(
            os.getenv(PROJECT_SYS_DIR_ROOT_ENV, self.root / ".meltano"),
        ).resolve()
        self.dotenv_file = dotenv_file

    def refresh(self, **kwargs: t.Any) -> None:
        """Refresh the project instance to reflect external changes.

        This should be called whenever env vars change, project files change,
        or other significant changes to the outside world occur.

        Args:
            kwargs: Keyword arguments for the new instance. These overwrite the
                defaults provided by the current instance. For example, if a
                Meltano environment has been activated, the project can be
                refreshed with this new environment by running
                `project.refresh(environment=environment)`.
        """
        kwargs = {
            "root": self.root,
            "environment": self.environment,
            "readonly": self.readonly,
            **kwargs,
        }
        cls = type(self)
        # Clear the dictionary backing `self` to invalidate outdated info,
        # cached properties, etc., then instantiate an up-to-date instance,
        # then steal its attributes to update the dictionary backing `self`.
        # This trick makes it as if the instance was just created, yet keeps
        # all existing references to it valid.
        self.__dict__.clear()
        self.__dict__.update(cls(**kwargs).__dict__)

    @cached_property
    def config_service(self) -> ConfigService:
        """Get the project config service.

        Returns:
            A `ConfigService` instance for this project.
        """
        return ConfigService(self)

    @cached_property
    def project_files(self) -> ProjectFiles:
        """Return a singleton `ProjectFiles` file manager instance.

        Returns:
            `ProjectFiles` file manager.
        """
        return ProjectFiles(root=self.root, meltano_file_path=self.meltanofile)

    @cached_property
    def settings(self) -> ProjectSettingsService:
        """Get the project settings.

        Returns:
            A `ProjectSettingsService` instance for this project.
        """
        return ProjectSettingsService(self)

    @cached_property
    def plugins(self) -> ProjectPluginsService:
        """Get the project plugins.

        Returns:
            A `ProjectPluginsService` instance for this project.
        """
        return ProjectPluginsService(self)

    @cached_property
    def hub_service(self) -> MeltanoHubService:
        """Get the Meltano Hub service.

        Returns:
            A `MeltanoHubService` instance for this project.
        """
        return MeltanoHubService(self)

    @cached_property
    def dirs(self) -> ProjectDirsService:
        """Get the project directories service.

        Returns:
            A `ProjectDirsService` instance for this project.
        """
        return ProjectDirsService.from_project(self)

    @cached_property
    def _meltano_interprocess_lock(self) -> fasteners.InterProcessLock:
        return fasteners.InterProcessLock(self.dirs.run().joinpath("meltano.yml.lock"))

    @property
    def user_agent(self) -> str:
        """Get the user agent for this project.

        Returns:
            the user agent string for this project
        """
        return f"Meltano/{get_meltano_version()}"

    @property
    def env(self) -> dict[str, str]:
        """Get environment variables for this project.

        Returns:
            dict of environment variables and values for this project.
        """
        environment_name = self.environment.name if self.environment else ""
        return {
            PROJECT_ROOT_ENV: str(self.root),
            PROJECT_ENVIRONMENT_ENV: environment_name,
            PROJECT_SYS_DIR_ROOT_ENV: str(self.sys_dir_root),
            MELTANO_USER_AGENT_ENV: self.user_agent,
        }

    @classmethod
    @fasteners.locked(lock="_activate_lock")
    def activate(cls, project: Project) -> None:
        """Activate the given Project.

        Args:
            project: the Project to activate

        Raises:
            OSError: if project cannot be activated due to unsupported OS
        """
        import ctypes

        check_meltano_compatibility(project.meltano.requires_meltano)

        # create a symlink to our current binary
        try:
            # check if running on Windows
            if os.name == "nt":
                executable = Path(sys.executable).parent / "meltano.exe"
                # Admin privileges are required to create symlinks on Windows
                if ctypes.windll.shell32.IsUserAnAdmin():  # type: ignore[attr-defined]
                    if executable.is_file():
                        project.dirs.run().joinpath("bin").symlink_to(executable)
                    else:
                        logger.warning(
                            "Could not create symlink: meltano.exe not "  # noqa: G004
                            f"present in {Path(sys.executable).parent!s}",
                        )
                else:
                    logger.debug(
                        "Failed to create symlink to 'meltano.exe': "
                        "administrator privilege required",
                    )
            else:
                executable = Path(sys.executable).parent / "meltano"
                if executable.is_file():
                    project.dirs.run().joinpath("bin").symlink_to(executable)
        except FileExistsError:
            pass
        except OSError as error:
            if error.errno == errno.EOPNOTSUPP:
                logger.warning(
                    f"Could not create symlink: {error}\nPlease make sure "  # noqa: G004
                    "that the underlying filesystem supports symlinks.",
                )
            else:
                raise

        logger.debug("Activated project at %s", project.root)

        # set the default project
        cls._default = project

    @classmethod
    def deactivate(cls) -> None:
        """Deactivate the given Project."""
        cls._default = None

    @property
    def file_version(self) -> int:
        """Get the version of Meltano found in this project's meltano.yml.

        Returns:
            the Project's meltano version
        """
        return self.meltano.version

    @classmethod
    @fasteners.locked(lock="_find_lock")
    def find(
        cls,
        project_root: Path | str | None = None,
        *,
        activate: bool = True,
        dotenv_file: Path | None = None,
    ) -> Project:
        """Find a Project.

        Args:
            project_root: The path to the root directory of the project. If not
                supplied, infer from PROJECT_ROOT_ENV or the current working
                directory and it's parents.
            activate: Save the found project so that future calls to `find`
                will continue to use this project.
            dotenv_file: The path to the .env file to use.

        Returns:
            the found project

        Raises:
            ProjectNotFound: if the provided `project_root` is not a Meltano
                project, or the current working directory is not a Meltano
                project or a subfolder of one.
        """
        if cls._default:
            return cls._default

        readonly = truthy(os.getenv(PROJECT_READONLY_ENV, "false"))

        if project_root := project_root or os.getenv(PROJECT_ROOT_ENV):
            project = Project(project_root, readonly=readonly, dotenv_file=dotenv_file)
            if not project.meltanofile.exists():
                raise ProjectNotFound(project)
        else:
            for directory in walk_parent_directories():
                project = Project(directory, readonly=readonly, dotenv_file=dotenv_file)
                if project.meltanofile.exists():
                    break
            if not project.meltanofile.exists():
                raise ProjectNotFound(Project(Path.cwd()))

        readonly = project.settings.get("project_readonly")
        if readonly != project.readonly:
            project.refresh(readonly=readonly)

        if activate:
            cls.activate(project)

        return project

    @property
    def meltano(self) -> MeltanoFileTypeHint:
        """Return a copy of the current meltano config.

        Raises:
            EmptyMeltanoFileException: The `meltano.yml` file is empty.

        Returns:
            The current meltano config.
        """
        from meltano.core.meltano_file import MeltanoFile

        conf: dict[str, t.Any] = yaml.load(self.meltanofile)
        if conf is None:
            raise EmptyMeltanoFileException

        with self._meltano_rw_lock.read_lock():
            return MeltanoFile.parse(self.project_files.load())

    @contextmanager
    def meltano_update(self) -> Generator[MeltanoFileTypeHint, None, None]:
        """Yield the current meltano configuration.

        Update the meltanofile if the context ends gracefully.

        Yields:
            the current meltano configuration

        Raises:
            ProjectReadonly: This project is readonly.
            Exception: The project files could not be updated.
        """
        if self.readonly:
            raise ProjectReadonly

        from meltano.core.meltano_file import MeltanoFile

        with self._meltano_rw_lock.write_lock(), self._meltano_interprocess_lock:
            meltano_config = MeltanoFile.parse(self.project_files.load())
            yield meltano_config
            try:
                self.project_files.update(meltano_config.canonical())  # type: ignore[arg-type]
            except Exception as err:  # pragma: no cover
                logger.critical("Could not update meltano.yml: %s", err)
                raise

        self.refresh()

    @deprecated(
        "Use `dirs.root_dir` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    def root_dir(self, *joinpaths: StrPath) -> Path:
        """Return the root directory of this project, optionally joined with path.

        Args:
            joinpaths: list of subdirs and/or file to join to project root.

        Returns:
            project root joined with provided subdirs and/or file
        """
        return self.dirs.root_dir(*joinpaths)

    @property
    def meltanofile(self) -> Path:
        """Get the path to this project's meltano.yml.

        Returns:
            the path to this project meltano.yml
        """
        return self.root.joinpath("meltano.yml")

    @property
    def dotenv(self) -> Path:
        """Get the path to this project's .env file.

        Returns:
            the path to this project's .env file
        """
        if self.dotenv_file:
            return (
                self.dotenv_file
                if self.dotenv_file.is_absolute()
                else self.root.joinpath(self.dotenv_file)
            )
        return self.root.joinpath(".env")

    @cached_property
    def dotenv_env(self) -> dict[str, str | None]:
        """Get values from this project's .env file.

        Returns:
            values found in this project's .env file
        """
        return dotenv_values(self.dotenv)

    def activate_environment(self, name: str) -> None:
        """Activate a Meltano environment.

        No-op if the active environment has the given name.

        Args:
            name: Name of the environment.
        """
        if getattr(self.environment, "name", object()) != name:
            self.refresh(environment=Environment.find(self.meltano.environments, name))
        logger.info(f"Environment {name!r} is active")  # noqa: G004

    def deactivate_environment(self) -> None:
        """Deactivate the currently active environment."""
        if self.environment is not None:
            self.refresh(environment=None)

    @contextmanager
    def dotenv_update(self) -> Generator[Path, None, None]:
        """Raise error if project is readonly.

        Used in context where .env files would be updated.

        Yields:
            the .env file

        Raises:
            ProjectReadonly: if the project is readonly
        """
        if self.readonly:
            raise ProjectReadonly

        yield self.dotenv
        self.refresh()

    @deprecated(
        "Use `dirs.meltano` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def meltano_dir(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:
        """Path to the project `.meltano` directory.

        Args:
            joinpaths: Paths to join to the `.meltano` directory.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `.meltano` dir optionally joined to given paths.
        """
        return self.dirs.meltano(*joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.venvs` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def venvs_dir(self, *prefixes: StrPath, make_dirs: bool = True) -> Path:
        """Path to a `venv` directory in `.meltano`.

        Args:
            prefixes: Paths to prepend to the `venv` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `venv` dir optionally prepended with given prefixes.
        """
        return self.dirs.venvs(*prefixes, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.run` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def run_dir(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:
        """Path to the `run` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `run` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `run` dir optionally joined to given paths.
        """
        return self.dirs.run(*joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.logs` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def logs_dir(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:
        """Path to the `logs` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `logs` directory in `.meltano`.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Resolved path to `logs` dir optionally joined to given paths.
        """
        return self.dirs.logs(*joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.job` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def job_dir(
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
        return self.dirs.job(state_id, *joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.job_logs` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def job_logs_dir(
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
        return self.dirs.job_logs(state_id, *joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.plugin` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def plugin_dir(
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
        return self.dirs.plugin(plugin, *joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.root_plugins` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
    @makedirs
    def root_plugins_dir(self, *joinpaths: StrPath, make_dirs: bool = True) -> Path:
        """Path to the project `plugins` directory.

        Args:
            joinpaths: Paths to join with the project `plugins` directory.
            make_dirs: Whether to create the directory hierarchy if it doesn't exist.

        Returns:
            Path to the project `plugins` directory.
        """
        return self.dirs.root_plugins(*joinpaths, make_dirs=make_dirs)

    @deprecated(
        "Use `dirs.plugin_lock_path` instead.",
        category=MeltanoInternalDeprecationWarning,
    )
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
        return self.dirs.plugin_lock_path(
            plugin_type,
            plugin_name,
            variant_name=variant_name,
            make_dirs=make_dirs,
        )

    def __eq__(self, other: object) -> bool:
        """Project equivalence check.

        Args:
            other: The other Project instance to check against.

        Returns:
            True if Projects are equal.
        """
        return self.root == getattr(other, "root", object())

    def __hash__(self) -> int:
        """Project hash.

        Returns:
            Project hash.
        """
        return self.root.__hash__()

    def __repr__(self) -> str:
        """Project representation.

        Returns:
            Project representation.
        """
        return f"Project({self.root!r})"
