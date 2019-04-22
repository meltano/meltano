import os
import yaml
import logging
import sys
from pathlib import Path
from typing import Union, Dict
from contextlib import contextmanager
from functools import wraps
from dotenv import load_dotenv

from .plugin import Plugin
from .error import Error


class ProjectNotFound(Error):
    def __init__(self):
        super().__init__(
            f"Cannot find `{os.getcwd()}/meltano.yml`. Are you in a meltano project?"
        )


class Project:
    """
    Represent the current Meltano project from a file-system
    perspective.
    """

    _meltano = {}

    def __init__(self, root: Union[Path, str] = None):
        self.root = Path(root or os.getcwd()).resolve()

    def activate(self):
        # helpful to refer to the current absolute project path
        os.environ["MELTANO_PROJECT_ROOT"] = str(self.root)

        load_dotenv(dotenv_path=self.root.joinpath(".env"))
        logging.debug(f"Activated project at {self.root}")

    def reload(self):
        """Force a reload from `meltano.yml`"""
        self._meltano = yaml.load(self.meltanofile.open()) or {}

    @classmethod
    def find(self, from_dir: Union[Path, str] = None, activate=True):
        project = Project(from_dir)

        if not project.meltanofile.exists():
            raise ProjectNotFound()

        if activate:
            project.activate()

        return project

    @property
    def meltano(self) -> Dict:
        """Return a copy of the current meltano config"""
        if not self._meltano:
            self.reload()

        return self._meltano.copy()

    @contextmanager
    def meltano_update(self):
        """
        Yield the current meltano configuration and update the meltanofile
        if the context ends gracefully.
        """
        try:
            meltano_update = self.meltano
            yield meltano_update

            # save it
            with self.meltanofile.open("w") as meltanofile:
                meltanofile.write(yaml.dump(meltano_update, default_flow_style=False))

            # update the cache
            self._meltano = meltano_update
        except Exception as err:
            logging.error(f"Could not update meltano.yml: {err}")
            raise

    def makedirs(func):
        @wraps(func)
        def decorate(*args, **kwargs):
            path = func(*args, **kwargs)

            # if there is an extension, only create the base dir
            _, ext = os.path.splitext(path)
            if ext:
                dir = os.path.dirname(path)
            else:
                dir = path

            os.makedirs(dir, exist_ok=True)
            return path

        return decorate

    def root_dir(self, *joinpaths):
        return self.root.joinpath(*joinpaths)

    @property
    def meltanofile(self):
        return self.root.joinpath("meltano.yml")

    @makedirs
    def meltano_dir(self, *joinpaths):
        return self.root.joinpath(".meltano", *joinpaths)

    @makedirs
    def venvs_dir(self, *prefixes):
        return self.meltano_dir(*prefixes, "venv")

    @makedirs
    def run_dir(self, *joinpaths):
        return self.meltano_dir("run", *joinpaths)

    @makedirs
    def model_dir(self, *joinpaths):
        return self.meltano_dir("models", *joinpaths)

    @makedirs
    def plugin_dir(self, plugin: Plugin, *joinpaths):
        return self.meltano_dir(plugin.type, plugin.name, *joinpaths)

    def __eq__(self, other):
        return self.root == other.root

    def __hash__(self):
        return self.root.__hash__()
