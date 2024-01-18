"""Manage Python virtual environments."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import platform
import shlex
import shutil
import subprocess
import sys
import typing as t
from functools import cached_property
from numbers import Number
from pathlib import Path

from meltano.core.error import AsyncSubprocessError, MeltanoError

if t.TYPE_CHECKING:
    from asyncio.subprocess import Process
    from collections.abc import Iterable

    from meltano.core.project import Project

logger = logging.getLogger(__name__)


class VirtualEnv:
    """Info about a single virtual environment."""

    _SUPPORTED_PLATFORMS = {
        "Linux",
        "Darwin",
        "Windows",
    }

    def __init__(
        self,
        root: Path,
        python: Path | str | None = None,
    ):
        """Initialize the `VirtualEnv` instance.

        Args:
            root: The root directory of the virtual environment.
            python: The path to the Python executable to use, or name to find on the
                $PATH. Defaults to the Python executable running Meltano.

        Raises:
            MeltanoError: The current system is not supported.
        """
        self._system = platform.system()
        if self._system not in self._SUPPORTED_PLATFORMS:
            raise MeltanoError(f"Platform {self._system!r} not supported.")
        self.root = root.resolve()
        self.python_path = self._resolve_python_path(python)

    @staticmethod
    def _resolve_python_path(python: Path | str | None) -> str:
        python_path: str | None = None

        if python is None:
            python_path = sys.executable
        elif isinstance(python, Path):
            python_path = str(python.resolve())
        elif isinstance(python, Number):
            raise MeltanoError(
                "Python must be specified as an executable name or path, "
                f"not the number {python!r}",
            )
        else:
            python_path = python if os.path.exists(python) else shutil.which(python)

        if python_path is None:
            raise MeltanoError(f"Python executable {python!r} was not found")

        if not os.access(python_path, os.X_OK):
            raise MeltanoError(f"{python_path!r} is not executable")

        return python_path

    @cached_property
    def lib_dir(self) -> Path:
        """Return the lib directory of the virtual environment.

        Raises:
            MeltanoError: The current system is not supported.

        Returns:
            The lib directory of the virtual environment.
        """
        if self._system in {"Linux", "Darwin"}:
            return self.root / "lib"
        elif self._system == "Windows":
            return self.root / "Lib"
        raise MeltanoError(f"Platform {self._system!r} not supported.")

    @cached_property
    def bin_dir(self) -> Path:
        """Return the bin directory of the virtual environment.

        Raises:
            MeltanoError: The current system is not supported.

        Returns:
            The bin directory of the virtual environment.
        """
        if self._system in {"Linux", "Darwin"}:
            return self.root / "bin"
        elif self._system == "Windows":
            return self.root / "Scripts"
        raise MeltanoError(f"Platform {self._system!r} not supported.")

    @cached_property
    def site_packages_dir(self) -> Path:
        """Return the site-packages directory of the virtual environment.

        Raises:
            MeltanoError: The current system is not supported.

        Returns:
            The site-packages directory of the virtual environment.
        """
        if self._system in {"Linux", "Darwin"}:
            return (
                self.lib_dir
                / f"python{'.'.join(str(x) for x in self.python_version_tuple[:2])}"
                / "site-packages"
            )
        elif self._system == "Windows":
            return self.lib_dir / "site-packages"
        raise MeltanoError(f"Platform {self._system!r} not supported.")

    @cached_property
    def python_version_tuple(self) -> tuple[int, int, int]:
        """Return the Python version tuple of the virtual environment.

        Returns:
            The Python version tuple of the virtual environment.
        """
        if self.python_path == sys.executable:
            return sys.version_info[:3]
        return t.cast(
            tuple[int, int, int],
            tuple(
                int(x)
                for x in subprocess.run(
                    (
                        self.python_path,
                        "-c",
                        "import sys; print(*sys.version_info[:3])",
                    ),
                    stdout=subprocess.PIPE,
                ).stdout.split(b" ")
            ),
        )


async def _extract_stderr(_):
    return None  # pragma: no cover


async def exec_async(*args, extract_stderr=_extract_stderr, **kwargs) -> Process:
    """Run an executable asynchronously in a subprocess.

    Args:
        args: Positional arguments for `asyncio.create_subprocess_exec`.
        extract_stderr: Async function that is provided the completed failed process,
            and returns its error string or `None`.
        kwargs: Keyword arguments for `asyncio.create_subprocess_exec`.

    Raises:
        AsyncSubprocessError: The command failed.

    Returns:
        The subprocess.
    """
    run = await asyncio.create_subprocess_exec(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )
    await run.wait()

    if run.returncode != 0:
        raise AsyncSubprocessError(
            "Command failed",
            process=run,
            stderr=await extract_stderr(run),
        )

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

    The methods in this class are not thread-safe.
    """

    def __init__(
        self,
        *,
        project: Project,
        python: Path | str | None = None,
        namespace: str = "",
        name: str = "",
    ):
        """Initialize the `VenvService`.

        Args:
            project: The Meltano project.
            python: The path to the Python executable to use, or name to find on $PATH.
                Defaults to the Python executable running Meltano.
            namespace: The namespace for the venv, e.g. a Plugin type.
            name: The name of the venv, e.g. a Plugin name.
        """
        self.project = project
        self.namespace = namespace
        self.name = name
        self.venv = VirtualEnv(
            self.project.venvs_dir(namespace, name),
            python or project.settings.get("python"),
        )
        self.plugin_fingerprint_path = self.venv.root / ".meltano_plugin_fingerprint"
        self.pip_log_path = self.project.logs_dir(
            "pip",
            self.namespace,
            self.name,
            "pip.log",
        ).resolve()

    async def install(
        self,
        pip_install_args: t.Sequence[str],
        clean: bool = False,
    ) -> None:
        """Configure a virtual environment, then run pip install with the given args.

        Args:
            pip_install_args: Arguments passed to `pip install`.
            clean: Whether to not attempt to use an existing virtual environment.
        """
        if not clean and self.requires_clean_install(pip_install_args):
            logger.debug(
                f"Packages for '{self.namespace}/{self.name}' have changed so "  # noqa: G004
                "performing a clean install.",
            )
            clean = True

        self.clean_run_files()

        await self._pip_install(pip_install_args=pip_install_args, clean=clean)
        self.write_fingerprint(pip_install_args)

    def requires_clean_install(self, pip_install_args: t.Sequence[str]) -> bool:
        """Determine whether a clean install is needed.

        Args:
            pip_install_args: The arguments being passed to `pip install`, used
                for fingerprinting the installation.

        Returns:
            Whether virtual environment doesn't exist or can't be reused.
        """

        def checks():  # A generator is used to perform the checks lazily
            # The Python installation used to create this venv no longer exists
            yield not self.exec_path("python").exists()
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
        logger.debug(f"Creating virtual environment for '{self.namespace}/{self.name}'")  # noqa: G004

        async def extract_stderr(proc: Process):
            return (await t.cast(asyncio.StreamReader, proc.stdout).read()).decode(
                "unicode_escape",
            )

        try:
            return await exec_async(
                sys.executable,
                "-m",
                "virtualenv",
                "--python",
                self.venv.python_path,
                str(self.venv.root),
                extract_stderr=extract_stderr,
            )
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                f"Could not create the virtualenv for '{self.namespace}/{self.name}'",
                process=err.process,
                stderr=await err.stderr,
            ) from err

    async def upgrade_pip(self) -> Process:
        """Upgrade the `pip` package to the latest version in the virtual environment.

        Raises:
            AsyncSubprocessError: Failed to upgrade pip to the latest version.

        Returns:
            The process running `pip install --upgrade ...`.
        """
        logger.debug(f"Upgrading pip for '{self.namespace}/{self.name}'")  # noqa: G004
        try:
            return await self._pip_install(("--upgrade", "pip"))
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(
                "Failed to upgrade pip to the latest version.",
                err.process,
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

    def write_fingerprint(self, pip_install_args: t.Sequence[str]) -> None:
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
        self,
        pip_install_args: t.Sequence[str],
        clean: bool = False,
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

        pip_install_args_str = shlex.join(pip_install_args)
        log_msg_prefix = (
            f"Upgrading with args {pip_install_args_str!r} in existing"
            if "--upgrade" in pip_install_args
            else f"Installing with args {pip_install_args_str!r} into"
        )
        logger.debug(
            f"{log_msg_prefix} virtual environment for '{self.namespace}/{self.name}'",  # noqa: G004
        )

        async def extract_stderr(proc: Process) -> str | None:  # pragma: no cover
            if not proc.stdout:
                return None

            return (await proc.stdout.read()).decode("unicode_escape")

        try:
            return await exec_async(
                str(self.exec_path("python")),
                "-m",
                "pip",
                "install",
                "--log",
                str(self.pip_log_path),
                *pip_install_args,
                extract_stderr=extract_stderr,
            )
        except AsyncSubprocessError as err:
            logger.info(
                "Logged pip install output to %s",  # noqa: WPS323
                self.pip_log_path,
            )
            raise AsyncSubprocessError(
                f"Failed to install plugin '{self.name}'.",
                err.process,
                stderr=await err.stderr,
            ) from err
