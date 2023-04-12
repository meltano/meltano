"""Meltano Projects."""


from __future__ import annotations

import errno
import logging
import os
import sys
import threading
import typing as t
from contextlib import contextmanager
from pathlib import Path

import fasteners
from dotenv import dotenv_values

from meltano.core import yaml
from meltano.core.behavior.versioned import Versioned
from meltano.core.config_service import ConfigService
from meltano.core.environment import Environment
from meltano.core.error import (
    EmptyMeltanoFileException,
    ProjectNotFound,
    ProjectReadonly,
)
from meltano.core.hub import MeltanoHubService
from meltano.core.plugin.base import PluginRef
from meltano.core.project_files import ProjectFiles
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import makedirs, sanitize_filename, truthy

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

if t.TYPE_CHECKING:
    from meltano.core.meltano_file import MeltanoFile as MeltanoFileTypeHint


logger = logging.getLogger(__name__)


PROJECT_ROOT_ENV = "MELTANO_PROJECT_ROOT"
PROJECT_ENVIRONMENT_ENV = "MELTANO_ENVIRONMENT"
PROJECT_READONLY_ENV = "MELTANO_PROJECT_READONLY"
PROJECT_SYS_DIR_ROOT_ENV = "MELTANO_SYS_DIR_ROOT"


def walk_parent_directories():
    """Yield each directory starting with the current up to the root.

    Yields:
        parent directories
    """
    directory = os.getcwd()
    while True:
        yield directory

        parent_directory = os.path.dirname(directory)
        if parent_directory == directory:
            return
        directory = parent_directory


class Project(Versioned):  # noqa: WPS214
    """Represents a Meltano project."""

    __version__ = 1
    _activate_lock = threading.Lock()
    _find_lock = threading.Lock()
    _meltano_rw_lock = fasteners.ReaderWriterLock()
    _default = None

    def __init__(
        self,
        root: os.PathLike,
        environment: Environment | None = None,
        readonly: bool = False,
    ):
        """Initialize a `Project` instance.

        Args:
            root: The root directory of the project.
            environment: The active Meltano environment.
            readonly: Whether the project is in read-only mode.
        """
        self.root = Path(root).resolve()
        self.environment: Environment | None = environment
        self.readonly = readonly
        self.sys_dir_root = Path(
            os.getenv(PROJECT_SYS_DIR_ROOT_ENV, self.root / ".meltano"),
        ).resolve()

    def refresh(self, **kwargs) -> None:
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
        cls = type(self)  # noqa: WPS117
        # Clear the dictionary backing `self` to invalidate outdated info,
        # cached properties, etc., then instantiate an up-to-date instance,
        # then steal its attributes to update the dictionary backing `self`.
        # This trick makes it as if the instance was just created, yet keeps
        # all existing references to it valid.
        self.__dict__.clear()
        self.__dict__.update(cls(**kwargs).__dict__)

    @cached_property
    def config_service(self):
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
    def settings(self):
        """Get the project settings.

        Returns:
            A `ProjectSettingsService` instance for this project.
        """
        return ProjectSettingsService(self)

    @cached_property
    def plugins(self):
        """Get the project plugins.

        Returns:
            A `ProjectPluginsService` instance for this project.
        """
        return ProjectPluginsService(self)

    @cached_property
    def hub_service(self):
        """Get the Meltano Hub service.

        Returns:
            A `MeltanoHubService` instance for this project.
        """
        return MeltanoHubService(self)

    @cached_property
    def _meltano_interprocess_lock(self):
        return fasteners.InterProcessLock(self.run_dir("meltano.yml.lock"))

    @property
    def env(self):
        """Get environment variables for this project.

        Returns:
            dict of environment variables and values for this project.
        """
        environment_name = self.environment.name if self.environment else ""
        return {
            PROJECT_ROOT_ENV: str(self.root),
            PROJECT_ENVIRONMENT_ENV: environment_name,
            PROJECT_SYS_DIR_ROOT_ENV: str(self.sys_dir_root),
        }

    @classmethod
    @fasteners.locked(lock="_activate_lock")
    def activate(cls, project: Project):
        """Activate the given Project.

        Args:
            project: the Project to activate

        Raises:
            OSError: if project cannot be activated due to unsupported OS
        """
        import ctypes

        project.ensure_compatible()

        # create a symlink to our current binary
        try:
            # check if running on Windows
            if os.name == "nt":
                executable = Path(sys.executable).parent / "meltano.exe"
                # Admin privileges are required to create symlinks on Windows
                if ctypes.windll.shell32.IsUserAnAdmin():
                    if executable.is_file():
                        project.run_dir().joinpath("bin").symlink_to(executable)
                    else:
                        logger.warning(
                            "Could not create symlink: meltano.exe not "
                            f"present in {str(Path(sys.executable).parent)}",
                        )
                else:
                    logger.warning(
                        "Failed to create symlink to 'meltano.exe': "
                        "administrator privilege required",
                    )
            else:
                executable = Path(sys.executable).parent / "meltano"
                if executable.is_file():
                    project.run_dir().joinpath("bin").symlink_to(executable)
        except FileExistsError:
            pass
        except OSError as error:
            if error.errno == errno.EOPNOTSUPP:
                logger.warning(
                    f"Could not create symlink: {error}\nPlease make sure "
                    "that the underlying filesystem supports symlinks.",
                )
            else:
                raise

        logger.debug(f"Activated project at {project.root}")

        # set the default project
        cls._default = project

    @classmethod
    def deactivate(cls):
        """Deactivate the given Project."""
        cls._default = None

    @property
    def file_version(self):
        """Get the version of Meltano found in this project's meltano.yml.

        Returns:
            the Project's meltano version
        """
        return self.meltano.version

    @classmethod
    @fasteners.locked(lock="_find_lock")
    def find(cls, project_root: Path | str | None = None, activate=True):
        """Find a Project.

        Args:
            project_root: The path to the root directory of the project. If not
                supplied, infer from PROJECT_ROOT_ENV or the current working
                directory and it's parents.
            activate: Save the found project so that future calls to `find`
                will continue to use this project.

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

        project_root = project_root or os.getenv(PROJECT_ROOT_ENV)
        if project_root:
            project = Project(project_root, readonly=readonly)
            if not project.meltanofile.exists():
                raise ProjectNotFound(project)
        else:
            for directory in walk_parent_directories():
                project = Project(directory, readonly=readonly)
                if project.meltanofile.exists():
                    break
            if not project.meltanofile.exists():
                raise ProjectNotFound(Project(os.getcwd()))

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
        from meltano.core.settings_service import FEATURE_FLAG_PREFIX, FeatureFlags

        conf: dict[str, t.Any] = yaml.load(self.meltanofile)
        if conf is None:
            raise EmptyMeltanoFileException

        lock = (
            self._meltano_rw_lock.write_lock
            if conf.get(f"{FEATURE_FLAG_PREFIX}.{FeatureFlags.ENABLE_UVICORN}", False)
            else self._meltano_rw_lock.read_lock
        )
        with lock():
            return MeltanoFile.parse(self.project_files.load())

    @contextmanager
    def meltano_update(self):
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
                self.project_files.update(meltano_config.canonical())
            except Exception as err:
                logger.critical("Could not update meltano.yml: %s", err)  # noqa: WPS323
                raise

        self.refresh()

    def root_dir(self, *joinpaths):
        """Return the root directory of this project, optionally joined with path.

        Args:
            joinpaths: list of subdirs and/or file to join to project root.

        Returns:
            project root joined with provided subdirs and/or file
        """
        return self.root.joinpath(*joinpaths)

    @property
    def meltanofile(self):
        """Get the path to this project's meltano.yml.

        Returns:
            the path to this project meltano.yml
        """
        return self.root.joinpath("meltano.yml")

    @property
    def dotenv(self):
        """Get the path to this project's .env file.

        Returns:
            the path to this project's .env file
        """
        return self.root.joinpath(".env")

    @property
    def dotenv_env(self):
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
        logger.info(f"Environment {name!r} is active")

    def deactivate_environment(self) -> None:
        """Deactivate the currently active environment."""
        if self.environment is not None:
            self.refresh(environment=None)

    @contextmanager
    def dotenv_update(self):
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

    @makedirs
    def meltano_dir(self, *joinpaths):
        """Path to the project `.meltano` directory.

        Args:
            joinpaths: Paths to join to the `.meltano` directory.

        Returns:
            Resolved path to `.meltano` dir optionally joined to given paths.
        """
        return self.sys_dir_root.joinpath(*joinpaths)

    @makedirs
    def analyze_dir(self, *joinpaths):
        """Path to the project `analyze` directory.

        Args:
            joinpaths: Paths to join to the `analyze` directory.

        Returns:
            Resolved path to `analyze` dir optionally joined to given paths.
        """
        return self.root_dir("analyze", *joinpaths)

    @makedirs
    def extract_dir(self, *joinpaths):
        """Path to the project `extract` directory.

        Args:
            joinpaths: Paths to join to the `extract` directory.

        Returns:
            Resolved path to `extract` dir optionally joined to given paths.
        """
        return self.root_dir("extract", *joinpaths)

    @makedirs
    def venvs_dir(self, *prefixes):
        """Path to a `venv` directory in `.meltano`.

        Args:
            prefixes: Paths to prepend to the `venv` directory in `.meltano`.

        Returns:
            Resolved path to `venv` dir optionally prepended with given prefixes.
        """
        return self.meltano_dir(*prefixes, "venv")

    @makedirs
    def run_dir(self, *joinpaths):
        """Path to the `run` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `run` directory in `.meltano`.

        Returns:
            Resolved path to `run` dir optionally joined to given paths.
        """
        return self.meltano_dir("run", *joinpaths)

    @makedirs
    def logs_dir(self, *joinpaths):
        """Path to the `logs` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `logs` directory in `.meltano`.

        Returns:
            Resolved path to `logs` dir optionally joined to given paths.
        """
        return self.meltano_dir("logs", *joinpaths)

    @makedirs
    def job_dir(self, state_id, *joinpaths):
        """Path to the `elt` directory in `.meltano/run`.

        Args:
            state_id: State ID of `run` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano`.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.run_dir("elt", sanitize_filename(state_id), *joinpaths)

    @makedirs
    def job_logs_dir(self, state_id, *joinpaths):
        """Path to the `elt` directory in `.meltano/logs`.

        Args:
            state_id: State ID of `logs` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano/logs`.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.logs_dir("elt", sanitize_filename(state_id), *joinpaths)

    @makedirs
    def plugin_dir(self, plugin: PluginRef, *joinpaths):
        """Path to the plugin installation directory in `.meltano`.

        Args:
            plugin: Plugin to retrieve or create directory for.
            joinpaths: Paths to join to the plugin installation directory in `.meltano`.

        Returns:
            Resolved path to plugin installation dir optionally joined to given paths.
        """
        return self.meltano_dir(plugin.type, plugin.name, *joinpaths)

    @makedirs
    def root_plugins_dir(self, *joinpaths: str):
        """Path to the project `plugins` directory.

        Args:
            joinpaths: Paths to join with the project `plugins` directory.

        Returns:
            Path to the project `plugins` directory.
        """
        return self.root_dir("plugins", *joinpaths)

    @makedirs
    def plugin_lock_path(
        self,
        plugin_type: str,
        plugin_name: str,
        variant_name: str | None = None,
    ):
        """Path to the project lock file.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.

        Returns:
            Path to the plugin lock file.
        """
        filename = f"{plugin_name}"

        if variant_name:
            filename = f"{filename}--{variant_name}"

        return self.root_plugins_dir(plugin_type, f"{filename}.lock")

    def __eq__(self, other):
        """Project equivalence check.

        Args:
            other: The other Project instance to check against.

        Returns:
            True if Projects are equal.
        """
        return self.root == getattr(other, "root", object())

    def __hash__(self):
        """Project hash.

        Returns:
            Project hash.
        """
        return self.root.__hash__()  # noqa: WPS609
