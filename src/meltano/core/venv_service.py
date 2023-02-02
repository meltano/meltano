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
from collections.abc import Iterable
from pathlib import Path

from meltano.core.error import AsyncSubprocessError
from meltano.core.project import Project

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

PLATFORM_SPECS = {"Linux": POSIX, "Darwin": POSIX, "Windows": NT}


def venv_platform_specs():
    """Get virtual environment sub-path info for the current platform.

    Raises:
        Exception: This platform is not supported.

    Returns:
        Virtual environment sub-path info for the current platform.
    """
    system = platform.system()
    try:
        return PLATFORM_SPECS[system]
    except KeyError as ex:
        raise Exception(f"Platform {system!r} not supported.") from ex


PIP_PACKAGES = ("pip", "setuptools==57.5.0", "wheel")


class VirtualEnv:
    """Info about a single virtual environment."""

    def __init__(self, root: Path):
        """Initialize the `VirtualEnv` instance.

        Args:
            root: The root directory of the virtual environment.
        """
        self.root = root.resolve()
        self.specs = venv_platform_specs()

    def __getattr__(self, key: str):
        """Get a specific attribute from this instance.

        Used to provide `VenvSpecs` attributes for this specific virtual environment.

        Args:
            key: The attribute name. Must be one of the `VenvSpecs` attributes.

        Returns:
            The root directory of this virtual environment joined to the requested
            platform-specific path using this platform's `VenvSpecs` instance.
        """
        return self.root / getattr(self.specs, key)

    def __str__(self):
        """_summary_.

        Returns:
            _description_.
        """
        return str(self.root)


async def exec_async(*args, **kwargs) -> Process:
    """Run an executable asyncronously in a subprocess.

    Args:
        args: Positional arguments for `asyncio.create_subprocess_exec`.
        kwargs: Keyword arguments for `asyncio.create_subprocess_exec`.

    Raises:
        AsyncSubprocessError: The command failed.

    Returns:
        The subprocess.
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


def fingerprint(pip_install_args: Iterable[str]) -> str:
    """Generate a hash identifying pip install args.

    Arguments are sorted and deduplicated before the hash is generated.

    Args:
        pip_install_args: Arguments for `pip install`.

    Returns:
        The SHA256 hash hex digest of the sorted set of pip install args.
    """
    return hashlib.sha256(" ".join(sorted(set(pip_install_args))).encode()).hexdigest()


class VenvService:  # noqa: WPS214
    """Manages virtual environments.

    The methods in this class are not threadsafe.
    """

    def __init__(self, project: Project, namespace: str = "", name: str = ""):
        """Initialize the `VenvService`.

        Args:
            project: The Meltano project.
            namespace: The namespace for the venv, e.g. a Plugin type.
            name: The name of the venv, e.g. a Plugin name.
        """
        self.project = project
        self.namespace = namespace
        self.name = name
        self.venv = VirtualEnv(self.project.venvs_dir(namespace, name))
        self.plugin_fingerprint_path = self.venv.root / ".meltano_plugin_fingerprint"

    async def install(self, pip_install_args: list[str], clean: bool = False) -> None:
        """Configure a virtual environment, then run pip install with the given args.

        Args:
            pip_install_args: Arguments passed to `pip install`.
            clean: Whether to not attempt to use an existing virtual environment.
        """
        if not clean and self.requires_clean_install(pip_install_args):
            logger.debug(
                f"Packages for '{self.namespace}/{self.name}' have changed so performing a clean install."
            )
            clean = True

        self.clean_run_files()
        await self._pip_install(pip_install_args=pip_install_args, clean=clean)
        self.write_fingerprint(pip_install_args)

    def requires_clean_install(self, pip_install_args: list[str]) -> bool:
        """Determine whether a clean install is needed.

        Args:
            pip_install_args: The arguments being passed to `pip install`, used
                for fingerprinting the installation.

        Returns:
            Whether virtual environment doesn't exist or can't be reused.
        """
        # A generator function is used to perform the checks lazily
        def checks():
            # The Python installation used to create this venv no longer exists
            yield not self.exec_path("python").exists()
            # The deprecated `meltano_venv.pth` feature is used by this venv
            yield self.venv.site_packages_dir.joinpath("meltano_venv.pth").exists()
            # The fingerprint of the venv does not match the pip install args
            existing_fingerprint = self.read_fingerprint()
            yield existing_fingerprint is None
            yield existing_fingerprint != fingerprint(pip_install_args)

        return any(checks())

    def clean_run_files(self) -> None:
        """Destroy cached configuration files, if they exist."""
        try:
            shutil.rmtree(self.project.run_dir(self.name, make_dirs=False))
        except FileNotFoundError:
            logger.debug("No cached configuration files to remove")

    def clean(self) -> None:
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

    async def create(self) -> Process:
        """Create a new virtual environment.

        Raises:
            AsyncSubprocessError: The virtual environment could not be created.

        Returns:
            The Python process creating the virtual environment.
        """
        logger.debug(f"Creating virtual environment for '{self.namespace}/{self.name}'")
        try:
            return await exec_async(sys.executable, "-m", "virtualenv", str(self.venv))
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Could not create the virtualenv for '{self.namespace}/{self.name}'",
                err.process,
            ) from err

    async def upgrade_pip(self) -> Process:
        """Upgrade the `pip` package to the latest version in the virtual environment.

        Raises:
            AsyncSubprocessError: Failed to upgrade pip to the latest version.

        Returns:
            The process running `pip install --upgrade ...`.
        """
        logger.debug(f"Upgrading pip for '{self.namespace}/{self.name}'")
        try:
            return await self._pip_install(["--upgrade", *PIP_PACKAGES])
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                "Failed to upgrade pip to the latest version.", err.process
            ) from err

    def read_fingerprint(self) -> str | None:
        """Get the fingerprint of the existing virtual environment.

        Returns:
            The fingerprint of the existing virtual environment if it exists.
            `None` otherwise.
        """
        if not self.plugin_fingerprint_path.exists():
            return None
        with open(self.plugin_fingerprint_path) as fingerprint_file:
            return fingerprint_file.read()

    def write_fingerprint(self, pip_install_args: list[str]) -> None:
        """Save the fingerprint for this installation.

        Args:
            pip_install_args: The arguments being passed to `pip install`.
        """
        with open(self.plugin_fingerprint_path, "w") as fingerprint_file:
            fingerprint_file.write(fingerprint(pip_install_args))

    def exec_path(self, executable: str) -> Path:
        """Return the absolute path for the given executable in the virtual environment.

        Args:
            executable: The path to the executable relative to the venv bin directory.

        Returns:
            The venv bin directory joined to the provided executable.
        """
        absolute_executable = self.venv.bin_dir / executable
        if platform.system() != "Windows":
            return absolute_executable

        # On Windows, try using the '.exe' suffixed version if it exists. Use the
        # regular executable path as a fallback (and for backwards compatibility).
        absolute_executable_windows = absolute_executable.with_suffix(".exe")
        return (
            absolute_executable_windows
            if absolute_executable_windows.exists()
            else absolute_executable
        )

    async def _pip_install(
        self, pip_install_args: list[str], clean: bool = False
    ) -> Process:
        """Install a package using `pip` in the proper virtual environment.

        Args:
            pip_install_args: The arguments to pass to `pip install`.
            clean: Whether the installation should be done in a clean venv.

        Raises:
            AsyncSubprocessError: The command failed.

        Returns:
            The process running `pip install` with the provided args.
        """
        if clean:
            self.clean()
            await self.create()
            await self.upgrade_pip()

        pip_install_args_str = " ".join(pip_install_args)
        log_msg_prefix = (
            f"Upgrading with args {pip_install_args_str!r} in existing"
            if "--upgrade" in pip_install_args
            else f"Installing with args {pip_install_args_str!r} into"
        )
        logger.debug(
            f"{log_msg_prefix} virtual environment for '{self.namespace}/{self.name}'"
        )

        try:
            return await exec_async(
                str(self.exec_path("python")), "-m", "pip", "install", *pip_install_args
            )
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Failed to install plugin '{self.name}'.", err.process
            ) from err
