"""Meltano Projects."""
import errno
import logging
import os
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Union

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
PROJECT_ENVIRONMENT_ENV = "MELTANO_ENVIRONMENT"
PROJECT_READONLY_ENV = "MELTANO_PROJECT_READONLY"


class ProjectNotFound(Error):
    """Occurs when a Project is instantiated outside of a meltano project structure."""

    def __init__(self, project):
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

    def __init__(self, root: Union[Path, str]):
        """Instantiate a Project from its root directory.

        Args:
            root: the root directory for the project
        """
        self.root = Path(root).resolve()
        self.readonly = False
        self._project_files = None
        self.__meltano_ip_lock = None

        self.active_environment: Optional[Environment] = None

    @property
    def _meltano_ip_lock(self):
        if self.__meltano_ip_lock is None:
            self.__meltano_ip_lock = fasteners.InterProcessLock(
                self.run_dir("meltano.yml.lock")
            )

        return self.__meltano_ip_lock

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
        }

    @classmethod
    @fasteners.locked(lock="_activate_lock")
    def activate(cls, project: "Project"):
        """Activate the given Project.

        Args:
            project: the Project to activate

        Raises:
            OSError: if project cannot be activated due to unsupported OS
        """
        project.ensure_compatible()

        # create a symlink to our current binary
        try:
            executable = Path(os.path.dirname(sys.executable), "meltano")
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

    @classmethod  # noqa: WPS231
    @fasteners.locked(lock="_find_lock")
    def find(cls, project_root: Union[Path, str] = None, activate=True):  # noqa: WPS231
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

    @property
    def project_files(self):
        """Return a singleton ProjectFiles file manager instance.

        Returns:
            ProjectFiles file manager
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
            the current meltano config
        """
        with self._meltano_rw_lock.read_lock():
            return MeltanoFile.parse(self.project_files.load())

    @contextmanager
    def meltano_update(self):
        """Yield the current meltano configuration.

        Update the meltanofile if the context ends gracefully.

        Yields:
            the current meltano configuration

        Raises:
            ProjectReadonly: if this project is readonly
            Exception: if project files could not be updated
        """
        if self.readonly:
            raise ProjectReadonly

        # fmt: off
        with self._meltano_rw_lock.write_lock(), self._meltano_ip_lock:

            meltano_config = MeltanoFile.parse(self.project_files.load())

            yield meltano_config

            try:
                meltano_config = self.project_files.update(meltano_config.canonical())
            except Exception as err:
                logger.critical("Could not update meltano.yml: %s", err)  # noqa: WPS323
                raise
        # fmt: on

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
            name: Name of the environment. Defaults to None.
        """
        self.active_environment = Environment.find(self.meltano.environments, name)

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
        """Path to the project `.meltano` directory."""
        return self.root.joinpath(".meltano", *joinpaths)  # noqa: DAR101,DAR201

    @makedirs
    def analyze_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the project `analyze` directory."""
        return self.root_dir("analyze", *joinpaths)  # noqa: DAR101,DAR201

    @makedirs
    def extract_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the project `extract` directory."""
        return self.root_dir("extract", *joinpaths)  # noqa: DAR101,DAR201

    @makedirs
    def venvs_dir(self, *prefixes, make_dirs: bool = True):
        """Path to a `venv` directory in `.meltano`."""
        return self.meltano_dir(  # noqa: DAR101,DAR201
            *prefixes, "venv", make_dirs=make_dirs
        )

    @makedirs
    def run_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the `run` directory in `.meltano`."""
        return self.meltano_dir(  # noqa: DAR101,DAR201
            "run", *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def logs_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the `logs` directory in `.meltano`."""
        return self.meltano_dir(  # noqa: DAR101,DAR201
            "logs", *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def job_dir(self, job_id, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/run`."""
        return self.run_dir(  # noqa: DAR101,DAR201
            "elt", secure_filename(job_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def job_logs_dir(self, job_id, *joinpaths, make_dirs: bool = True):
        """Path to the `elt` directory in `.meltano/logs`."""
        return self.logs_dir(  # noqa: DAR101,DAR201
            "elt", secure_filename(job_id), *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def model_dir(self, *joinpaths, make_dirs: bool = True):
        """Path to the `models` directory in `.meltano`."""
        return self.meltano_dir(  # noqa: DAR101,DAR201
            "models", *joinpaths, make_dirs=make_dirs
        )

    @makedirs
    def plugin_dir(self, plugin: PluginRef, *joinpaths, make_dirs: bool = True):
        """Path to the plugin installation directory in `.meltano`."""
        return self.meltano_dir(  # noqa: DAR101,DAR201
            plugin.type, plugin.name, *joinpaths, make_dirs=make_dirs
        )

    def __eq__(self, other):  # noqa: D105
        return (  # noqa: DAR101,DAR201
            hasattr(other, "root") and self.root == other.root  # noqa: WPS421
        )

    def __hash__(self):  # noqa: D105
        return self.root.__hash__()  # noqa: DAR101,DAR201,WPS609
