"""Meltano Project management."""

from __future__ import annotations

import errno
import logging
import os
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

import fasteners
from dotenv import dotenv_values
from werkzeug.utils import secure_filename

from meltano.core.environment import Environment
from meltano.core.plugin.base import PluginRef

from .behavior.versioned import Versioned
from .error import Error
from .meltano_file import MeltanoFile
from .project_files import ProjectFiles
from .utils import makedirs, truthy

logger = logging.getLogger(__name__)


PROJECT_ROOT_ENV = "MELTANO_PROJECT_ROOT"
PROJECT_READONLY_ENV = "MELTANO_PROJECT_READONLY"


class ProjectNotFound(Error):
    """Error raised when no Meltano project was detected."""

    def __init__(self, project):
        """Initialize exception.

        Args:
            project: A Meltano project.
        """
        super().__init__(
            f"Cannot find `{project.meltanofile}`. Are you in a meltano project?"
        )


class ProjectReadonly(Error):
    """Error raised when the user tries to modify a read-only project."""

    def __init__(self):
        """Initialize exception."""
        super().__init__("This Meltano project is deployed as read-only")


def walk_parent_directories():
    """Yield each directory starting with the current up to the root.

    Yields:
        Parent directories.
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

    def __init__(self, root: Path | str):
        """Initialize project.

        Args:
            root: Root directory of the project.
        """
        self.root = Path(root).resolve()
        self.readonly = False
        self._project_files = None
        self.__meltano_ip_lock = None

        self.active_environment: Environment | None = None

    @property
    def _meltano_ip_lock(self):
        if self.__meltano_ip_lock is None:
            self.__meltano_ip_lock = fasteners.InterProcessLock(
                self.run_dir("meltano.yml.lock")
            )

        return self.__meltano_ip_lock

    @property
    def env(self):
        """Return a dictionary of project environment variables.

        Returns:
            A dictionary of environment variables.
        """
        return {PROJECT_ROOT_ENV: str(self.root)}

    @classmethod
    @fasteners.locked(lock="_activate_lock")
    def activate(cls, project: Project):
        """Activate a project.

        Args:
            project: A Meltano project.

        Raises:
            OSError: If a symbolic link cannot be created.
        """
        project.ensure_compatible()

        # create a symlink to our current binary
        try:
            executable = Path(os.path.dirname(sys.executable), "meltano")
            if executable.is_file():
                project.run_dir().joinpath("bin").symlink_to(executable)
        except FileExistsError:
            pass
        except OSError as err:
            if err.errno == errno.EOPNOTSUPP:
                logger.warning(
                    f"Could not create symlink: {err}\nPlease make sure that the underlying filesystem supports symlinks."
                )
            else:
                raise

        logger.debug(f"Activated project at {project.root}")

        # set the default project
        cls._default = project

    @classmethod
    def deactivate(cls):
        """Deactivate the default project."""
        cls._default = None

    @property
    def file_version(self):
        """Return the version of the project file.

        Returns:
            The version of the project file.
        """
        return self.meltano.version

    @classmethod  # noqa: WPS231
    @fasteners.locked(lock="_find_lock")
    def find(cls, project_root: Path | str = None, activate=True):  # noqa: WPS231
        """Find a Project.

        Args:
            project_root: The path to the root directory of the project. If not
                supplied, infer from PROJECT_ROOT_ENV or the current working directory
                and its parents.
            activate: Save the found project so that future calls to `find` will
                continue to use this project.

        Raises:
            ProjectNotFound: if the provided `project_root` is not a Meltano project,
                or the current working directory is not a Meltano project or a subfolder
                of one.

        Returns:
            A Meltano project.
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

    @property
    def project_files(self):
        """Return a singleton ProjectFiles file manager instance.

        Returns:
            A singleton ProjectFiles file manager instance.
        """
        if self._project_files is None:
            self._project_files = ProjectFiles(
                root=self.root, meltano_file_path=self.meltanofile
            )
        return self._project_files

    @property
    def meltano(self) -> MeltanoFile:
        """Return a copy of the current meltano config.

        Returns:
            A copy of the current meltano config.
        """
        with self._meltano_rw_lock.read_lock():
            return MeltanoFile.parse(self.project_files.load())

    @contextmanager
    def meltano_update(self):
        """Update the Meltano project files.

        Yield the current meltano configuration and update the meltanofile if the
        context ends gracefully.

        Raises:
            Exception: If the context ends with an exception.
            ProjectReadonly: If the project is read-only.

        Yields:
            The Meltano project contents.
        """
        if self.readonly:
            raise ProjectReadonly

        with self._meltano_rw_lock.write_lock(), self._meltano_ip_lock:

            meltano_config = MeltanoFile.parse(self.project_files.load())

            yield meltano_config

            try:
                meltano_config = self.project_files.update(meltano_config.canonical())
            except Exception as err:
                logger.critical(f"Could not update meltano.yml: {err}")
                raise

    def root_dir(self, *joinpaths: str):
        """Return the path to a directory relative to the project root.

        Args:
            joinpaths: Paths to join with the project root.

        Returns:
            The path to the joined directory.
        """
        return self.root.joinpath(*joinpaths)

    @contextmanager
    def file_update(self):
        """Update the Meltano project files.

        Raises:
            ProjectReadonly: If the project is read-only.

        Yields:
            The Meltano project root path.
        """
        if self.readonly:
            raise ProjectReadonly

        yield self.root

    @property
    def meltanofile(self):
        """Return the path to the Meltano file.

        Returns:
            The path to the Meltano file.
        """
        return self.root.joinpath("meltano.yml")

    @property
    def dotenv(self):
        """Return the path to the .env file.

        Returns:
            The path to the .env file.
        """
        return self.root.joinpath(".env")

    @property
    def dotenv_env(self):
        """Return the environment variables from the .env file.

        Returns:
            The environment variables from the .env file.
        """
        return dotenv_values(self.dotenv)

    def activate_environment(self, name: str) -> None:
        """Retrieve an environment configuration.

        Args:
            name: Name of the environment. Defaults to None.
        """
        self.active_environment = Environment.find(self.meltano.environments, name)

    @contextmanager
    def dotenv_update(self):
        """Update the .env file.

        Raises:
            ProjectReadonly: if the project is readonly.

        Yields:
            The .env file path.
        """
        if self.readonly:
            raise ProjectReadonly

        yield self.dotenv

    @makedirs
    def meltano_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the project `.meltano` directory.

        Args:
            joinpaths: Paths to join with the project `.meltano` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            The path to the project `.meltano` directory.
        """
        return self.root.joinpath(".meltano", *joinpaths)

    @makedirs
    def analyze_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the project `analyze` directory.

        Args:
            joinpaths: Paths to join with the project `analyze` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the project `analyze` directory.
        """
        return self.root_dir("analyze", *joinpaths)

    @makedirs
    def extract_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the project `extract` directory.

        Args:
            joinpaths: Paths to join with the project `extract` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the project `extract` directory.
        """
        return self.root_dir("extract", *joinpaths)

    @makedirs
    def venvs_dir(self, *prefixes: str, make_dirs: bool = True):
        """Path to a `venv` directory in `.meltano`.

        Args:
            prefixes: Prefixes to use to create the `venv` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the `venv` directory.
        """
        return self.meltano_dir(*prefixes, "venv", make_dirs=make_dirs)

    @makedirs
    def run_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the `run` directory in `.meltano`.

        Args:
            joinpaths: Paths to join with the `run` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the `run` directory in `.meltano`.
        """
        return self.meltano_dir("run", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def logs_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the `logs` directory in `.meltano`.

        Args:
            joinpaths: Paths to join with the `logs` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the `logs` directory in `.meltano`.
        """
        return self.meltano_dir("logs", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def job_dir(self, job_id: str, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/run`.

        Args:
            job_id: The job id.
            joinpaths: Paths to join with the `elt` job directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            The path to the `elt` job directory.
        """
        return self.run_dir(
            "elt", secure_filename(job_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def job_logs_dir(self, job_id: str, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/logs`.

        Args:
            job_id: The job id.
            joinpaths: Paths to join with the `elt` logs directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the `elt` logs directory.
        """
        return self.logs_dir(
            "elt", secure_filename(job_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def model_dir(self, *joinpaths: str, make_dirs: bool = True):
        """Path to the `models` directory in `.meltano`.

        Args:
            joinpaths: Paths to join with the `models` directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the `models` directory in `.meltano`.
        """
        return self.meltano_dir("models", *joinpaths, make_dirs=make_dirs)

    @makedirs
    def plugin_dir(self, plugin: PluginRef, *joinpaths, make_dirs: bool = True):
        """Path to the plugin installation directory in `.meltano`.

        Args:
            plugin: The Meltano plugin.
            joinpaths: Paths to join with the plugin installation directory.
            make_dirs: If True, create the directory hierarchy if it does not exist.

        Returns:
            Path to the plugin installation directory in `.meltano`.
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
            f"{filename}.json",
            make_dirs=make_dirs,
        )

    def __eq__(self, other):
        """Equality check.

        Args:
            other: The other project object to compare.

        Returns:
            True if the other project object is equal to this one.
        """
        return self.root == other.root

    def __hash__(self):
        """Hash function.

        Returns:
            The hash of the project.
        """
        return self.root.__hash__()  # noqa: WPS609
