import os
import yaml
import logging
from pathlib import Path
from typing import Union, Dict
from contextlib import contextmanager
from functools import wraps

from .plugin import Plugin


class Project:
    """
    Represent the current Meltano project from a file-system
    perspective.
    """

    _meltano = {}

    def __init__(self, root: Union[Path, str]):
        self.root = Path(root)

    def chdir(self):
        os.chdir(self.root)
        self.root = Path(".")

    @classmethod
    def find(self, from_dir: Union[Path, str] = ".", chdir=True):
        """
        Recursively search for a `meltano.yml` file. Once found,
        return a `Project` correct dir.
        """
        cwd = os.getcwd()

        while not Project(".").meltanofile.exists():
            if os.getcwd() == "/":
                raise Exception("Cannot go any further.")

            os.chdir("..")

        if not chdir:
            os.chdir(cwd)

        return Project(os.getcwd())

    @property
    def meltano(self) -> Dict:
        """Return a copy of the current meltano config"""
        if not self._meltano:
            self._meltano = yaml.load(self.meltanofile.open()) or {}
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
    def plugin_dir(self, plugin: Plugin, *joinpaths):
        return self.meltano_dir(plugin.type, plugin.name, *joinpaths)
