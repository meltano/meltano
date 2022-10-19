"""Meltano Projects."""

from __future__ import annotations

import errno
import logging
import os
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import fasteners
from cached_property import cached_property
from dotenv import dotenv_values
from werkzeug.utils import secure_filename

from meltano.core import yaml
from meltano.core.behavior.versioned import Versioned
from meltano.core.environment import Environment
from meltano.core.error import EmptyMeltanoFileException, Error
from meltano.core.plugin.base import PluginRef
from meltano.core.project_files import ProjectFiles
from meltano.core.utils import makedirs, truthy

if TYPE_CHECKING:
    from .meltano_file import MeltanoFile as MeltanoFileTypeHint


logger = logging.getLogger(__name__)


PROJECT_ROOT_ENV = "MELTANO_PROJECT_ROOT"
PROJECT_ENVIRONMENT_ENV = "MELTANO_ENVIRONMENT"
PROJECT_READONLY_ENV = "MELTANO_PROJECT_READONLY"
PROJECT_SYS_DIR_ROOT = "MELTANO_SYS_DIR_ROOT"


class ProjectNotFound(Error):
    """Occurs when a Project is instantiated outside of a meltano project structure."""

    def __init__(self, project: Project):
        """Instantiate the error.

        Args:
            project: the name of the project which cannot be found
        """
        super().__init__(
            f"Cannot find `{project.meltanofile}`. Are you in a meltano project?"
        )


class ProjectReadonly(Error):
    """Occurs when attempting to update a readonly project."""

    def __init__(self):
        """Instantiate the error."""
        super().__init__("This Meltano project is deployed as read-only")


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
    """Represent the current Meltano project from a file-system perspective."""

    __version__ = 1
    _activate_lock = threading.Lock()
    _find_lock = threading.Lock()
    _meltano_rw_lock = fasteners.ReaderWriterLock()
    _default = None

    def __init__(self, root: os.PathLike):
        """Instantiate a Project from its root directory.

        Args:
            root: the root directory for the project
        """
        self.root = Path(root).resolve()
        self.sys_dir_root = Path(
            os.getenv(PROJECT_SYS_DIR_ROOT, self.root / ".meltano")
        ).resolve()
        self.readonly = False
        self.active_environment: Environment | None = None

    @cached_property
    def _meltano_interprocess_lock(self):
        return fasteners.InterProcessLock(self.run_dir("meltano.yml.lock"))

    @property
    def env(self):
        """Get environment variables for this project.

        Returns:
            dict of environment variables and values for this project.
        """
        environment_name = (
            self.active_environment.name if self.active_environment else ""
        )
        return {
            PROJECT_ROOT_ENV: str(self.root),
            PROJECT_ENVIRONMENT_ENV: environment_name,
            PROJECT_SYS_DIR_ROOT: str(self.sys_dir_root),
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
                        logger.warn(
                            "Could not create symlink: meltano.exe not "
                            f"present in {str(Path(sys.executable).parent)}"
                        )
                else:
                    logger.warn(
                        "Failed to create symlink to 'meltano.exe': "
                        "administrator privilege required"
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
                    f"Could not create symlink: {error}\nPlease make sure that the underlying filesystem supports symlinks."
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
    def find(cls, project_root: Path | str = None, activate=True):
        """Find a Project.

        Args:
            project_root: The path to the root directory of the project. If not supplied,
                infer from PROJECT_ROOT_ENV or the current working directory and it's parents.
            activate: Save the found project so that future calls to `find` will
                continue to use this project.

        Returns:
            the found project

        Raises:
            ProjectNotFound: if the provided `project_root` is not a Meltano project, or
                the current working directory is not a Meltano project or a subfolder of one.
        """
        if cls._default:
            return cls._default

        project_root = project_root or os.getenv(PROJECT_ROOT_ENV)
        if project_root:
            project = Project(project_root)
            if not project.meltanofile.exists():
                raise ProjectNotFound(project)
        else:
            for directory in walk_parent_directories():
                project = Project(directory)
                if project.meltanofile.exists():
                    break
            if not project.meltanofile.exists():
                raise ProjectNotFound(Project(os.getcwd()))

        # if we activate a project using `find()`, it should
        # be set as the default project for future `find()`
        if activate:
            cls.activate(project)

        if truthy(os.getenv(PROJECT_READONLY_ENV, "false")):
            project.readonly = True

        return project

    @cached_property
    def project_files(self) -> ProjectFiles:
        """Return a singleton `ProjectFiles` file manager instance.

        Returns:
            `ProjectFiles` file manager.
        """
        return ProjectFiles(root=self.root, meltano_file_path=self.meltanofile)

    def clear_cache(self) -> None:
        """Clear cached project files (e.g. `meltano.yml`).

        This can be useful if the cached `ProjectFiles` object has been
        modified in-place, but not updated on-disk, and you need the on-disk
        version.
        """
        try:
            del self.__dict__["project_files"]
        except KeyError:
            pass

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

        conf: dict[str, Any] = yaml.load(self.meltanofile)
        if conf is None:
            raise EmptyMeltanoFileException()

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

    def root_dir(self, *joinpaths):
        """Return the root directory of this project, optionally joined with path.

        Args:
            joinpaths: list of subdirs and/or file to join to project root.

        Returns:
            project root joined with provided subdirs and/or file
        """
        return self.root.joinpath(*joinpaths)

    @contextmanager
    def file_update(self):
        """Raise error if project is readonly.

        Used in context where project files would be updated.

        Yields:
            the project root

        Raises:
            ProjectReadonly: if the project is readonly
        """
        if self.readonly:
            raise ProjectReadonly

        yield self.root

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
        """Retrieve an environment configuration.

        Args:
            name: Name of the environment.
        """
        self.active_environment = Environment.find(self.meltano.environments, name)
        logger.info(f"Environment {name!r} is active")

    def deactivate_environment(self) -> None:
        """Deactivate the currently active environment."""
        self.active_environment = None

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

    @makedirs
    def meltano_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the project `.meltano` directory.

        Args:
            joinpaths: Paths to join to the `.meltano` directory.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `.meltano` dir optionally joined to given paths.
        """
        return self.sys_dir_root.joinpath(*joinpaths)

    @makedirs
    def analyze_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the project `analyze` directory.

        Args:
            joinpaths: Paths to join to the `analyze` directory.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `analyze` dir optionally joined to given paths.
        """
        return self.root_dir("analyze", *joinpaths)

    @makedirs
    def extract_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the project `extract` directory.

        Args:
            joinpaths: Paths to join to the `extract` directory.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `extract` dir optionally joined to given paths.
        """
        return self.root_dir("extract", *joinpaths)

    @makedirs
    def venvs_dir(self, *prefixes, make_dirs: bool = True):
        """Path to a `venv` directory in `.meltano`.

        Args:
            prefixes: Paths to prepend to the `venv` directory in `.meltano`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `venv` dir optionally prepended with given prefixes.
        """
        return self.meltano_dir(*prefixes, "venv", make_dirs=make_dirs)

    @makedirs
    def run_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the `run` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `run` directory in `.meltano`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `run` dir optionally joined to given paths.
        """
        return self.meltano_dir("run", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def logs_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the `logs` directory in `.meltano`.

        Args:
            joinpaths: Paths to join to the `logs` directory in `.meltano`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `logs` dir optionally joined to given paths.
        """
        return self.meltano_dir("logs", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def job_dir(self, state_id, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/run`.

        Args:
            state_id: State ID of `run` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.run_dir(
            "elt", secure_filename(state_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def job_logs_dir(self, state_id, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/logs`.

        Args:
            state_id: State ID of `logs` dir.
            joinpaths: Paths to join to the `elt` directory in `.meltano/logs`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to `elt` dir optionally joined to given paths.
        """
        return self.logs_dir(
            "elt", secure_filename(state_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def plugin_dir(self, plugin: PluginRef, *joinpaths, make_dirs: bool = True):
        """Path to the plugin installation directory in `.meltano`.

        Args:
            plugin: Plugin to retrieve or create directory for.
            joinpaths: Paths to join to the plugin installation directory in `.meltano`.
            make_dirs: Flag to make directories if not exists.

        Returns:
            Resolved path to plugin installation dir optionally joined to given paths.
        """
        return self.meltano_dir(
            plugin.type, plugin.name, *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def root_plugins_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the project `plugins` directory.

        Args:
            joinpaths: Paths to join with the project `plugins` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

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
        make_dirs: bool = True,
    ):
        """Path to the project lock file.

        Args:
            plugin_type: The plugin type.
            plugin_name: The plugin name.
            variant_name: The plugin variant name.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the plugin lock file.
        """
        filename = f"{plugin_name}"

        if variant_name:
            filename = f"{filename}--{variant_name}"

        return self.root_plugins_dir(
            plugin_type,
            f"{filename}.lock",
            make_dirs=make_dirs,
        )

    def __eq__(self, other):
        """Project equivalence check.

        Args:
            other: The other Project instance to check against.

        Returns:
            True if Projects are equal.
        """
        return hasattr(other, "root") and self.root == other.root  # noqa: WPS421

    def __hash__(self):
        """Project hash.

        Returns:
            Project hash.
        """
        return self.root.__hash__()  # noqa: WPS609
