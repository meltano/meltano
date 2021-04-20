import asyncio
import logging
import os
import platform
import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

from .error import SubprocessError
from .project import Project

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


class VenvServiceFactory:
    def __init__(self, project):
        self.project = project

    def create(self, namespace="", name=""):
        return VenvService(self.project, namespace, name)


class VenvService:
    def __init__(self, project, namespace="", name=""):
        """
        VenvService manages isolated virtual environments.

        The methods in this class are not threadsafe.

        """
        self.project = project
        self.namespace = namespace
        self.name = name
        self.venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        self.python_path = str(self.venv.bin_dir.joinpath("python"))

    async def clean_install(self, *pip_urls):
        """
        Wipe and recreate a virtual environment and install the given
        `pip_urls` packages in it.

        :raises: SubprocessError: if any of the commands fail.
        """
        self.clean()
        await self.create()
        await self.upgrade_pip()
        await asyncio.gather(*[self.install(pip_url) for pip_url in pip_urls])

    def clean(self):
        """
        Destroy the virtual environment, if it exists.
        """
        try:
            shutil.rmtree(str(self.venv))
            logger.debug("Removed old virtual environment")
        except FileNotFoundError:
            # If the VirtualEnv has never been created before do nothing
            logger.debug("No old virtual environment to remove")
            pass

        return

    async def create(self):
        """
        Create a new virtual environment.

        :raises: SubprocessError: if the command fails.
        """
        logger.debug("Creating virtual environment")
        run = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "venv",
            str(self.venv),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        await run.wait()

        if run.returncode != 0:
            stderr = await run.stderr.read()
            raise SubprocessError(
                f"Could not create the virtualenv for '{self.namespace}/{self.name}'",
                run,
                stderr=stderr,
            )

        return run

    async def upgrade_pip(self):
        """
        Upgrade the `pip` package to the latest version in the virtual environment.

        :raises: SubprocessError: if the command fails.
        """
        logger.debug("Upgrading pip")
        run = await asyncio.create_subprocess_exec(
            self.python_path,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        await run.wait()

        if run.returncode != 0:
            stderr = await run.stderr.read()
            raise SubprocessError(
                f"Failed to upgrade pip to the latest version.", run, stderr=stderr
            )

        return run

    async def install(self, pip_url):
        """
        Install a package using `pip` in the proper virtual environment.

        :raises: SubprocessError: if the command fails.
        """

        meltano_pth_path = self.venv.site_packages_dir.joinpath("meltano_venv.pth")
        if meltano_pth_path.exists():
            os.remove(meltano_pth_path)

        logger.debug("Installing into new virtual environment")
        run = await asyncio.create_subprocess_exec(
            self.python_path,
            "-m",
            "pip",
            "install",
            *pip_url.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        await run.wait()

        if run.returncode != 0:
            stderr = await run.stderr.read()
            raise SubprocessError(
                f"Failed to install plugin '{self.name}'.", run, stderr=stderr
            )

        return run

    def exec_path(self, bin, name=None, namespace=""):
        name = name or bin
        venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        return venv.bin_dir.joinpath(bin)
