"""Manage Python virtual environments."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import platform
import shutil
import subprocess
import sys
from asyncio.subprocess import Process
from collections import namedtuple
from pathlib import Path

from .error import AsyncSubprocessError
from .project import Project

logger = logging.getLogger(__name__)

VenvSpecs = namedtuple("VenvSpecs", ("lib_dir", "bin_dir", "site_packages_dir"))

POSIX = VenvSpecs(
    lib_dir="lib",
    bin_dir="bin",
    site_packages_dir=os.path.join(
        "lib",
        f"python{'.'.join(str(part) for part in sys.version_info[:2])}",
        "site-packages",
    ),
)

NT = VenvSpecs(
    lib_dir="Lib",
    bin_dir="Scripts",
    site_packages_dir=os.path.join("Lib", "site-packages"),
)

PIP_PACKAGES = ("pip", "setuptools==57.5.0", "wheel")


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


def fingerprint(pip_urls: list[str]):
    """Return a unique string for the given pip urls."""
    key = " ".join(sorted(pip_urls))
    return hashlib.sha256(bytes(key, "utf-8")).hexdigest()


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
        self.python_path = self.venv.bin_dir.joinpath("python")
        self.plugin_fingerprint_path = self.venv.root.joinpath(
            ".meltano_plugin_fingerprint"
        )

    async def install(self, *pip_urls: str, clean: bool = False):
        """
        Configure a virtual environment and install the given `pip_urls` packages in it.

        This will try to use an existing virtual environment if one exists unless commanded
        to `clean`.
        """
        pip_urls = [pip_url for arg in pip_urls for pip_url in arg.split(" ")]

        if not clean and self.requires_clean_install(pip_urls):
            logger.debug(
                f"Packages for '{self.namespace}/{self.name}' have changed so performing a clean install."
            )
            clean = True

        self.clean_run_files()

        if clean:
            await self._clean_install(pip_urls)
        else:
            await self._upgrade_install(pip_urls)
        self.write_fingerprint(pip_urls)

    def requires_clean_install(self, pip_urls: list[str]) -> bool:
        """Return `True` if the virtual environment doesn't exist or can't be reused."""
        meltano_pth_path = self.venv.site_packages_dir.joinpath("meltano_venv.pth")
        if meltano_pth_path.exists():
            # clean up deprecated feature
            return True
        existing_fingerprint = self.read_fingerprint()
        if not existing_fingerprint:
            return True
        return existing_fingerprint != fingerprint(pip_urls)

    def clean_run_files(self):
        """Destroy cached configuration files, if they exist."""
        try:
            shutil.rmtree(self.project.run_dir(self.name, make_dirs=False))
        except FileNotFoundError:
            logger.debug("No cached configuration files to remove")

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

    async def create(self):
        """Create a new virtual environment."""
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
        """Upgrade the `pip` package to the latest version in the virtual environment."""
        logger.debug(f"Upgrading pip for '{self.namespace}/{self.name}'")

        try:
            return await self._pip_install(*PIP_PACKAGES, upgrade=True)

        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                "Failed to upgrade pip to the latest version.", err.process
            )

    def read_fingerprint(self) -> str | None:
        """Return the fingerprint of the existing virtual environment, if any."""
        if not self.plugin_fingerprint_path.exists():
            return None
        with open(self.plugin_fingerprint_path) as fingerprint_file:
            return fingerprint_file.read()

    def write_fingerprint(self, pip_urls: list[str]):
        """Save the fingerprint for this installation."""
        with open(self.plugin_fingerprint_path, "wt") as fingerprint_file:
            fingerprint_file.write(fingerprint(pip_urls))

    def exec_path(self, executable: str) -> Path:
        """Return the absolute path for the given binary in the virtual environment."""
        return self.venv.bin_dir.joinpath(executable)

    async def _clean_install(self, pip_urls: list[str]):
        self.clean()
        await self.create()
        await self.upgrade_pip()

        logger.debug(
            f"Installing '{' '.join(pip_urls)}' into virtual environment for '{self.namespace}/{self.name}'"  # noqa: WPS221
        )
        await self._pip_install(*pip_urls)

    async def _upgrade_install(self, pip_urls: list[str]):
        logger.debug(
            f"Upgrading '{' '.join(pip_urls)}' in existing virtual environment for '{self.namespace}/{self.name}'"  # noqa: WPS221
        )
        await self._pip_install(*PIP_PACKAGES, *pip_urls, upgrade=True)

    async def _pip_install(self, *pip_urls: str, upgrade: bool = False):
        """
        Install a package using `pip` in the proper virtual environment.

        :raises: AsyncSubprocessError: if the command fails.
        """
        args = [
            str(self.python_path),
            "-m",
            "pip",
            "install",
        ]
        if upgrade:
            args += ["--upgrade"]
        args += pip_urls

        try:
            return await exec_async(*args)
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Failed to install plugin '{self.name}'.", err.process
            )
