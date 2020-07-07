import fasteners
import logging
import os
import sys
import threading
import yaml
from copy import deepcopy
from contextlib import contextmanager
from dotenv import dotenv_values
from functools import wraps
from pathlib import Path
from typing import Union, Dict
from atomicwrites import atomic_write

from .error import Error
from .behavior.versioned import Versioned
from .utils import makedirs, slugify
from .meltano_file import MeltanoFile

PROJECT_ROOT_ENV = "MELTANO_PROJECT_ROOT"


class ProjectNotFound(Error):
    def __init__(self, project):
        super().__init__(
            f"Cannot find `{project.meltanofile}`. Are you in a meltano project?"
        )


class Project(Versioned):
    """
    Represent the current Meltano project from a file-system
    perspective.
    """

    __version__ = 1
    _activate_lock = threading.Lock()
    _find_lock = threading.Lock()
    _meltano_rw_lock = fasteners.ReaderWriterLock()
    _default = None

    def __init__(self, root: Union[Path, str]):
        self.root = Path(root).resolve()
        self._meltano_ip_lock = fasteners.InterProcessLock(
            self.run_dir("meltano.yml.lock")
        )

    @property
    def env(self):
        return {PROJECT_ROOT_ENV: str(self.root)}

    @classmethod
    @fasteners.locked(lock="_activate_lock")
    def activate(cls, project: "Project"):
        project.ensure_compatible()

        # create a symlink to our current binary
        try:
            executable = Path(os.path.dirname(sys.executable), "meltano")
            if executable.is_file():
                project.run_dir().joinpath("bin").symlink_to(executable)
        except FileExistsError:
            pass

        logging.debug(f"Activated project at {project.root}")

        # set the default project
        cls._default = project

    @classmethod
    def deactivate(cls):
        cls._default = None

    @property
    def file_version(self):
        return self.meltano.version

    @classmethod
    @fasteners.locked(lock="_find_lock")
    def find(cls, project_root: Union[Path, str] = None, activate=True):
        if cls._default:
            return cls._default

        project_root = project_root or os.getenv(PROJECT_ROOT_ENV) or os.getcwd()
        project = Project(project_root)

        if not project.meltanofile.exists():
            raise ProjectNotFound(project)

        # if we activate a project using `find()`, it should
        # be set as the default project for future `find()`
        if activate:
            cls.activate(project)

        return project

    @property
    def meltano(self) -> Dict:
        """Return a copy of the current meltano config"""
        # fmt: off
        with self._meltano_rw_lock.read_lock(), \
             self.meltanofile.open() as meltanofile:
            return MeltanoFile.parse(yaml.safe_load(meltanofile))
        # fmt: on

    @contextmanager
    def meltano_update(self):
        """
        Yield the current meltano configuration and update the meltanofile
        if the context ends gracefully.
        """
        # fmt: off
        with self._meltano_rw_lock.write_lock(), \
            self._meltano_ip_lock:

            with self.meltanofile.open() as meltanofile:
                # read the latest version
                meltano_update = MeltanoFile.parse(yaml.safe_load(meltanofile))

            yield meltano_update

            try:
                with atomic_write(self.meltanofile, overwrite=True) as meltanofile:
                    # update if everything is fine
                    yaml.dump(meltano_update, meltanofile, default_flow_style=False, sort_keys=False)
            except Exception as err:
                logging.critical(f"Could not update meltano.yml: {err}")
                raise
        # fmt: on

    def root_dir(self, *joinpaths):
        return self.root.joinpath(*joinpaths)

    @property
    def meltanofile(self):
        return self.root.joinpath("meltano.yml")

    @property
    def dotenv(self):
        return self.root.joinpath(".env")

    @makedirs
    def meltano_dir(self, *joinpaths):
        return self.root.joinpath(".meltano", *joinpaths)

    @makedirs
    def analyze_dir(self, *joinpaths):
        return self.root_dir("analyze", *joinpaths)

    @makedirs
    def extract_dir(self, *joinpaths):
        return self.root_dir("extract", *joinpaths)

    @makedirs
    def venvs_dir(self, *prefixes):
        return self.meltano_dir(*prefixes, "venv")

    @makedirs
    def run_dir(self, *joinpaths):
        return self.meltano_dir("run", *joinpaths)

    @makedirs
    def job_dir(self, job_id, *joinpaths):
        return self.run_dir("elt", slugify(job_id), *joinpaths)

    @makedirs
    def model_dir(self, *joinpaths):
        return self.meltano_dir("models", *joinpaths)

    @makedirs
    def plugin_dir(self, plugin: "PluginRef", *joinpaths):
        return self.meltano_dir(plugin.type, plugin.name, *joinpaths)

    def __eq__(self, other):
        return self.root == other.root

    def __hash__(self):
        return self.root.__hash__()
