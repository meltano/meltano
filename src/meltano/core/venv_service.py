import subprocess
import platform
import sys
import shutil
import os
import logging
from pathlib import Path
from collections import namedtuple

from .project import Project
from .error import SubprocessError


logger = logging.getLogger(__name__)

VenvSpecs = namedtuple("VenvSpecs", ("lib_dir", "bin_dir", "site_packages_dir"))

POSIX = VenvSpecs(
    lib_dir="lib",
    bin_dir="bin",
    site_packages_dir=os.path.join("lib", f"python{sys.version[:3]}", "site-packages"),
)

NT = VenvSpecs(
    lib_dir="Lib",
    bin_dir="Scripts",
    site_packages_dir=os.path.join("Lib", "site-packages"),
)


class VirtualEnv:
    PLATFORM_SPECS = {"Linux": POSIX, "Darwin": POSIX, "Windows": NT}

    def __init__(self, root: Path):
        self.root = root
        self._specs = self.__class__.platform_specs()

    @classmethod
    def platform_specs(cls):
        try:
            system = platform.system()
            return cls.PLATFORM_SPECS[system]
        except KeyError:
            raise Exception(f"Platform {system} not supported.")

    def __getattr__(self, attr):
        spec = getattr(self._specs, attr)
        return self.root.joinpath(spec)

    def __str__(self):
        return str(self.root)


class VenvService:
    def __init__(self, project):
        self.project = project

    def clean(self, namespace="", name=""):
        venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        try:
            shutil.rmtree(str(venv))
            logger.debug("Removed old virtual environment")
        except FileNotFoundError:
            # If the VirtualEnv has never been created before do nothing
            logger.debug("No old virtual environment to remove")
            pass

        return

    def create(self, namespace="", name=""):
        venv = VirtualEnv(self.project.venvs_dir(namespace, name))

        logger.debug("Creating virtual environment")
        venv_run = subprocess.run(
            [sys.executable, "-m", "venv", str(venv)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if venv_run.returncode != 0:
            raise SubprocessError(
                f"Could not create of the virtualenv for '{namespace}/{name}'", venv_run
            )

        python_path = venv.bin_dir.joinpath("python")

        upgrade_run = subprocess.run(
            [
                str(python_path),
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
                "setuptools",
                "wheel",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if upgrade_run.returncode != 0:
            raise SubprocessError(
                f"Failed to upgrade pip to the latest version.", upgrade_run
            )

        return venv_run

    def install(self, pip_url, namespace="", name=""):
        """
        Install a package using `pip` in the proper virtual environment.

        This method is not threadsafe.
        """

        venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        python_path = venv.bin_dir.joinpath("python")

        meltano_pth_path = venv.site_packages_dir.joinpath("meltano_venv.pth")
        if meltano_pth_path.exists():
            os.remove(meltano_pth_path)

        logger.debug("Installing into new virtual environment")
        run = subprocess.run(
            [str(python_path), "-m", "pip", "install", *pip_url.split(" ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if run.returncode != 0:
            raise SubprocessError(f"Failed to install plugin '{name}'.", run)

        return run

    def exec_path(self, bin, name=None, namespace=""):
        name = name or bin
        venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        return venv.bin_dir.joinpath(bin)
