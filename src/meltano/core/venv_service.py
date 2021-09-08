"""Manage Python virtual environments."""
import asyncio
import logging
import os
import platform
import shutil
import subprocess
import sys
from asyncio.subprocess import Process
from collections import namedtuple
from pathlib import Path
from types import TracebackType
from typing import Callable, Tuple, Type

from .error import AsyncSubprocessError
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


def log_rmtree_error(
    op: Callable,
    path: Path,
    exc_info: Tuple[Type[BaseException], BaseException, TracebackType],
):
    """Log an exception when shutil.rmtree fails.

    Args:
        op: OS operation that failed
        path: Directory path
        exc_info: Exception raised by shutil.rmtree
    """
    logger.debug(
        "Failed to remove directory tree %s", path, exc_info=exc_info  # noqa: WPS323
    )


class VirtualEnv:
    PLATFORM_SPECS = {"Linux": POSIX, "Darwin": POSIX, "Windows": NT}

    def __init__(self, root: Path):
        self.root = root
        self._specs = self.__class__.platform_specs()

    @classmethod
    def platform_specs(cls):
        system = platform.system()
        try:
            return cls.PLATFORM_SPECS[system]
        except KeyError:
            raise Exception(f"Platform {system} not supported.")

    def __getattr__(self, attr):
        spec = getattr(self._specs, attr)
        return self.root.joinpath(spec)

    def __str__(self):
        return str(self.root)


async def exec_async(*args, **kwargs) -> Process:
    """
    Run an executable asyncronously.

    :raises AsyncSubprocessError: if the command fails
    """
    run = await asyncio.create_subprocess_exec(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )
    await run.wait()

    if run.returncode != 0:
        raise AsyncSubprocessError("Command failed", run)

    return run


class VenvService:
    def __init__(self, project: Project, namespace: str = "", name: str = ""):
        """
        Manage isolated virtual environments.

        The methods in this class are not threadsafe.
        """
        self.project = project
        self.namespace = namespace
        self.name = name
        self.venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        self.python_path = str(self.venv.bin_dir.joinpath("python"))

    async def clean_install(self, *pip_urls):
        """
        Wipe and recreate a virtual environment and install the given `pip_urls` packages in it.

        :raises: SubprocessError: if any of the commands fail.
        """
        self.clean()
        self.clean_run_files()
        await self.create()
        await self.upgrade_pip()
        await asyncio.gather(*[self.install(pip_url) for pip_url in pip_urls])

    def clean_run_files(self):
        """Destroy cached configuration files, if they exist."""
        shutil.rmtree(
            self.project.run_dir(self.name, make_dirs=False), onerror=log_rmtree_error
        )

    def clean(self):
        """Destroy the virtual environment, if it exists."""
        try:
            shutil.rmtree(self.venv.root)
            logger.debug(
                "Removed old virtual environment for '%s/%s'",  # noqa: WPS323
                self.namespace,
                self.name,
            )
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
        logger.debug(f"Creating virtual environment for '{self.namespace}/{self.name}'")
        try:
            return await exec_async(
                sys.executable,
                "-m",
                "venv",
                str(self.venv),
            )
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Could not create the virtualenv for '{self.namespace}/{self.name}'",
                err.process,
            )

    async def upgrade_pip(self):
        """
        Upgrade the `pip` package to the latest version in the virtual environment.

        :raises: SubprocessError: if the command fails.
        """
        logger.debug(f"Upgrading pip for '{self.namespace}/{self.name}'")
        try:
            return await exec_async(
                self.python_path,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
                "setuptools==57.5.0",
                "wheel",
            )
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                "Failed to upgrade pip to the latest version.", err.process
            )

    async def install(self, pip_url: str):
        """
        Install a package using `pip` in the proper virtual environment.

        :raises: AsyncSubprocessError: if the command fails.
        """
        meltano_pth_path = self.venv.site_packages_dir.joinpath("meltano_venv.pth")
        if meltano_pth_path.exists():
            os.remove(meltano_pth_path)

        logger.debug(
            f"Installing '{pip_url}' into virtual environment for '{self.namespace}/{self.name}'"
        )
        try:
            return await exec_async(
                self.python_path,
                "-m",
                "pip",
                "install",
                *pip_url.split(" "),
            )
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Failed to install plugin '{self.name}'.", err.process
            )

    def exec_path(self, executable):
        """Return the absolute path for the given binary in the virtual environment."""
        return self.venv.bin_dir.joinpath(executable)
