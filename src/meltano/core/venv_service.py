"""Manage Python virtual environments."""

from __future__ import annotations

import asyncio
import hashlib
import json
import platform
import shlex
import shutil
import subprocess
import sys
import typing as t
from asyncio.subprocess import Process
from collections.abc import Awaitable, Callable
from functools import cache, cached_property

import structlog

from meltano.core.error import AsyncSubprocessError, MeltanoError

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Sequence
    from pathlib import Path

    from meltano.core.plugin.project_plugin import ProjectPlugin
    from meltano.core.project import Project

if sys.version_info >= (3, 11):
    from typing import Self  # noqa: ICN003
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override


logger = structlog.stdlib.get_logger(__name__)

StdErrExtractor: t.TypeAlias = Callable[[Process], Awaitable[str | None]]


@cache
def find_uv() -> str:
    """Find the `uv` executable.

    Tries to import the `uv` package and use its `find_uv_bin` function to find the
    `uv` executable. If that fails, falls back to using the `uv` executable on the
    system PATH. If it can't be found on the PATH, returns `"uv"`.

    Adapted from https://github.com/wntrblm/nox/blob/55c7eaf2eb03feb4a4b79e74966c542b75d61401/nox/virtualenv.py#L42-L54.

    Copyright 2016 Alethea Katherine Flowers

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Returns:
        A string representing the path to the `uv` executable.

    Raises:
        MeltanoError: The `uv` executable could not be found.
    """
    from uv import find_uv_bin

    return find_uv_bin()


class VirtualEnv:
    """Info about a single virtual environment."""

    _SUPPORTED_PLATFORMS: t.ClassVar[set[str]] = {
        "Linux",
        "Darwin",
        "Windows",
    }

    def __init__(
        self,
        root: Path,
        *,
        python: str | None = None,
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
            raise MeltanoError(f"Platform {self._system!r} not supported.")  # noqa: EM102, TRY003
        self.root = root.resolve()
        self.python_path = python or sys.executable
        self.plugin_fingerprint_path = self.root / ".meltano_plugin_fingerprint"

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
        if self._system == "Windows":
            return self.root / "Lib"
        raise MeltanoError(f"Platform {self._system!r} not supported.")  # noqa: EM102, TRY003

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
        if self._system == "Windows":
            return self.root / "Scripts"
        raise MeltanoError(f"Platform {self._system!r} not supported.")  # noqa: EM102, TRY003

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
        if self._system == "Windows":
            return self.lib_dir / "site-packages"
        raise MeltanoError(f"Platform {self._system!r} not supported.")  # noqa: EM102, TRY003

    @cached_property
    def python_version_tuple(self) -> tuple[int, int, int]:
        """Return the Python version tuple of the virtual environment.

        Returns:
            The Python version tuple of the virtual environment.
        """
        if self.python_path == sys.executable:
            return sys.version_info[:3]
        return t.cast(
            "tuple[int, int, int]",
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

    def get_fingerprint(self, pip_install_args: Sequence[str]) -> str:
        """Compute the fingerprint of the virtual environment.

        Args:
            pip_install_args: The arguments being passed to `pip install`.

        Returns:
            The fingerprint of the virtual environment.
        """
        return fingerprint(pip_install_args, self.python_path)

    def read_fingerprint(self) -> str | None:
        """Get the fingerprint of the existing virtual environment.

        Returns:
            The fingerprint of the existing virtual environment if it exists.
            `None` otherwise.
        """
        if not self.plugin_fingerprint_path.exists():
            return None
        return self.plugin_fingerprint_path.read_text()

    def write_fingerprint(self, pip_install_args: Sequence[str]) -> None:
        """Save the fingerprint for this installation.

        Args:
            pip_install_args: The arguments being passed to `pip install`.
        """
        self.plugin_fingerprint_path.write_text(self.get_fingerprint(pip_install_args))

    def exec_path(self, executable: str) -> Path:
        """Return the absolute path for the given executable in the virtual environment.

        Args:
            executable: The path to the executable relative to the venv bin directory.

        Returns:
            The venv bin directory joined to the provided executable.
        """
        absolute_executable = self.bin_dir / executable
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

    def requires_install(self, pip_install_args: Sequence[str]) -> bool:
        """Determine whether a clean install is needed.

        Args:
            pip_install_args: The arguments being passed to `pip install`.

        Returns:
            Whether the virtual environment needs to be installed.
        """

        # A generator is used to perform the checks lazily
        def checks() -> Generator[bool, None, None]:
            # The Python installation used to create this venv no longer exists
            yield not self.exec_path("python").exists()
            # The fingerprint of the venv does not match the pip install args
            existing_fingerprint = self.read_fingerprint()
            yield existing_fingerprint is None
            yield existing_fingerprint != self.get_fingerprint(pip_install_args)

        return any(checks())


async def _extract_stderr(_) -> None:
    return None  # pragma: no cover


async def exec_async(*args, extract_stderr=_extract_stderr, **kwargs) -> Process:  # noqa: ANN001, ANN002, ANN003
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
        raise AsyncSubprocessError(  # noqa: TRY003
            "Command failed",  # noqa: EM101
            process=run,
            stderr=await extract_stderr(run),
        )

    return run


def fingerprint(pip_install_args: Iterable[str], interpreter: str | None = None) -> str:
    """Generate a hash identifying pip install args and Python interpreter.

    Arguments are sorted and deduplicated before the hash is generated.

    Args:
        pip_install_args: Arguments for `pip install`.
        interpreter: Python interpreter (path or command name).

    Returns:
        The SHA256 hash hex digest of the sorted set of pip install args and Python.
    """
    components = sorted(set(pip_install_args))
    # Only include Python interpreter in fingerprint if it's different from default
    # This ensures backward compatibility while detecting Python version changes
    if interpreter and interpreter != sys.executable:
        components.append(f"python:{interpreter}")
    return hashlib.sha256(" ".join(components).encode()).hexdigest()


class VenvService:
    """Manages virtual environments.

    The methods in this class are not thread-safe.
    """

    def __init__(
        self,
        *,
        project: Project,
        python: str | None = None,
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
            self.project.dirs.venvs(namespace, name, make_dirs=False),
            python=python or project.settings.get("python"),
        )

    @classmethod
    def from_plugin(cls, project: Project, plugin: ProjectPlugin) -> Self:
        """Create a service instance from a project and plugin.

        Args:
            project: The Meltano project.
            plugin: The plugin to create a service instance for.

        Returns:
            A service instance.
        """
        return cls(
            project=project,
            python=plugin.python,
            namespace=plugin.type,
            name=plugin.plugin_dir_name,
        )

    @property
    def install_log_path(self) -> Path:
        """Return the path to the install log file.

        Returns:
            The path to the install log file.
        """
        return self.project.logs_dir(
            "pip",
            self.namespace,
            self.name,
            "install.log",
        ).resolve()

    async def install(
        self,
        pip_install_args: Sequence[str],
        *,
        clean: bool = False,
        env: dict[str, str | None] | None = None,
    ) -> None:
        """Configure a virtual environment, then run pip install with the given args.

        Args:
            pip_install_args: Arguments passed to `pip install`.
            clean: Whether to not attempt to use an existing virtual environment.
            env: Environment variables to pass to the subprocess.
        """
        if not clean and self.requires_clean_install(pip_install_args):
            logger.debug(
                f"Packages for '{self.namespace}/{self.name}' have changed so "  # noqa: G004
                "performing a clean install.",
            )
            clean = True

        self.clean_run_files()

        await self._pip_install(pip_install_args=pip_install_args, clean=clean, env=env)
        self.venv.write_fingerprint(pip_install_args)

    def requires_clean_install(self, pip_install_args: Sequence[str]) -> bool:
        """Determine whether a clean install is needed.

        Args:
            pip_install_args: The arguments being passed to `pip install`, used
                for fingerprinting the installation.

        Returns:
            Whether virtual environment doesn't exist or can't be reused.
        """
        return self.venv.requires_install(pip_install_args)

    def clean_run_files(self) -> None:
        """Destroy cached configuration files, if they exist."""
        run_dir = self.project.dirs.run(self.name, make_dirs=False)

        try:
            for path in run_dir.iterdir():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        except FileNotFoundError:
            logger.debug("No cached configuration files to remove")

    def clean(self) -> None:
        """Destroy the virtual environment, if it exists."""
        try:
            shutil.rmtree(self.venv.root)
            logger.debug(
                "Removed old virtual environment for '%s/%s'",
                self.namespace,
                self.name,
            )
        except FileNotFoundError:
            # If the VirtualEnv has never been created before do nothing
            logger.debug("No old virtual environment to remove")

    async def create_venv(
        self,
        *,
        extract_stderr: StdErrExtractor = _extract_stderr,
    ) -> Process:
        """Create a new virtual environment.

        Args:
            extract_stderr: Async function that is provided the completed failed
                process, and returns its error string or `None`.

        Returns:
            The Python process creating the virtual environment.
        """
        return await exec_async(
            sys.executable,
            "-m",
            "virtualenv",
            f"--python={self.venv.python_path}",
            str(self.venv.root),
            extract_stderr=extract_stderr,
        )

    async def create(self) -> Process:
        """Create a new virtual environment.

        Raises:
            AsyncSubprocessError: The virtual environment could not be created.

        Returns:
            The Python process creating the virtual environment.
        """
        logger.debug(f"Creating virtual environment for '{self.namespace}/{self.name}'")  # noqa: G004

        async def extract_stderr(proc: Process):  # noqa: ANN202
            return (await t.cast("asyncio.StreamReader", proc.stdout).read()).decode(
                "utf-8",
                errors="replace",
            )

        try:
            return await self.create_venv(extract_stderr=extract_stderr)
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(  # noqa: TRY003
                f"Could not create the virtualenv for '{self.namespace}/{self.name}'",  # noqa: EM102
                process=err.process,
                stderr=await err.stderr,
            ) from err

    async def upgrade_installer(
        self,
        *,
        env: dict[str, str | None] | None = None,
    ) -> Process | None:
        """Upgrade the `pip` package to the latest version in the virtual environment.

        Args:
            env: Environment variables to pass to the subprocess.

        Raises:
            AsyncSubprocessError: Failed to upgrade pip to the latest version.

        Returns:
            The process running `pip install --upgrade ...`.
        """
        logger.debug(f"Upgrading pip for '{self.namespace}/{self.name}'")  # noqa: G004
        try:
            return await self._pip_install(("--upgrade", "pip"), env=env)
        except AsyncSubprocessError as err:
            raise AsyncSubprocessError(  # noqa: TRY003
                "Failed to upgrade pip to the latest version.",  # noqa: EM101
                err.process,
            ) from err

    def exec_path(self, executable: str) -> Path:
        """Return the absolute path for the given executable in the virtual environment.

        Args:
            executable: The path to the executable relative to the venv bin directory.

        Returns:
            The venv bin directory joined to the provided executable.
        """
        return self.venv.exec_path(executable)

    async def install_pip_args(
        self,
        pip_install_args: Sequence[str],
        *,
        extract_stderr: StdErrExtractor = _extract_stderr,
        env: dict[str, str | None] | None = None,
    ) -> Process:
        """Return the `pip install` arguments to use.

        Args:
            pip_install_args: The arguments to pass to `pip install`.
            extract_stderr: Async function that is provided the completed failed
                process, and returns its error string or `None`.
            env: Environment variables to pass to the subprocess.

        Returns:
            The process running `pip install` with the provided args.
        """
        return await exec_async(
            str(self.exec_path("python")),
            "-m",
            "pip",
            "install",
            "--log",
            str(self.install_log_path),
            *pip_install_args,
            extract_stderr=extract_stderr,
            env=env,
        )

    async def uninstall_package(self, package: str) -> Process:
        """Uninstall a single package.

        Args:
            package: The package name.

        Returns:
            The process running `pip uninstall` with the provided package.
        """
        return await exec_async(
            str(self.exec_path("python")),
            "-m",
            "pip",
            "uninstall",
            "--yes",
            package,
            extract_stderr=_extract_stderr,
        )

    async def _pip_install(
        self,
        pip_install_args: Sequence[str],
        *,
        clean: bool = False,
        env: dict[str, str | None] | None = None,
    ) -> Process:
        """Install a package using `pip` in the proper virtual environment.

        Args:
            pip_install_args: The arguments to pass to `pip install`.
            clean: Whether the installation should be done in a clean venv.
            env: Environment variables to pass to the subprocess.

        Raises:
            AsyncSubprocessError: The command failed.

        Returns:
            The process running `pip install` with the provided args.
        """
        if clean:
            self.clean()
            await self.create()
            await self.upgrade_installer(env=env)

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

            return (await proc.stdout.read()).decode("utf-8", errors="replace")

        return await self.install_pip_args(
            pip_install_args,
            extract_stderr=extract_stderr,
            env=env,
        )

    async def list_installed(self, *args: str) -> list[dict[str, t.Any]]:
        """List the installed dependencies."""
        proc = await exec_async(
            str(self.exec_path("python")),
            "-m",
            "pip",
            "list",
            "--format=json",
            *args,
        )
        stdout, _ = await proc.communicate()
        return json.loads(stdout)


class UvVenvService(VenvService):
    """Manages virtual environments using `uv`."""

    def __init__(self, *args: t.Any, **kwargs: t.Any):
        """Initialize the `UvVenvService`.

        Args:
            args: Positional arguments for the VenvService.
            kwargs: Keyword arguments for the VenvService.
        """
        super().__init__(*args, **kwargs)
        self.uv = find_uv()
        logger.debug("Using uv executable at %s", self.uv)

    @override
    async def upgrade_installer(
        self,
        *,
        env: dict[str, str | None] | None = None,
    ) -> Process | None:
        """No-op for `uv` virtual environments.

        Args:
            env: Environment variables to pass to the subprocess.
        """

    @override
    async def install_pip_args(
        self,
        pip_install_args: Sequence[str],
        *,
        extract_stderr: StdErrExtractor = _extract_stderr,
        env: dict[str, str | None] | None = None,
    ) -> Process:
        """Run `pip install` in the plugin's virtual environment.

        Args:
            pip_install_args: The arguments to pass to `pip install`.
            extract_stderr: Async function that is provided the completed failed
                process, and returns its error string or `None`.
            env: Environment variables to pass to the subprocess.

        Returns:
            The process running `pip install` with the provided args.
        """
        return await exec_async(
            self.uv,
            "pip",
            "install",
            f"--python={self.exec_path('python')}",
            *pip_install_args,
            extract_stderr=extract_stderr,
            env=env,
        )

    @override
    async def uninstall_package(self, package: str) -> Process:
        """Uninstall a single package using `uv`.

        Args:
            package: The package name.

        Returns:
            The process running `pip uninstall` with the provided package.
        """
        return await exec_async(
            self.uv,
            "pip",
            "uninstall",
            f"--python={self.exec_path('python')}",
            package,
        )

    @override
    async def create_venv(
        self,
        *,
        extract_stderr: StdErrExtractor = _extract_stderr,
    ) -> Process:
        """Create a new virtual environment using `uv`.

        Args:
            extract_stderr: Async function that is provided the completed failed
                process, and returns its error string or `None`.

        Returns:
            The Python process creating the virtual environment.
        """
        return await exec_async(
            self.uv,
            "venv",
            f"--python={self.venv.python_path}",
            str(self.venv.root),
            extract_stderr=extract_stderr,
        )

    @override
    async def list_installed(self, *args: str) -> list[dict[str, t.Any]]:
        """List the installed dependencies."""
        proc = await exec_async(
            self.uv,
            "pip",
            "list",
            "--quiet",
            "--format=json",
            f"--python={self.exec_path('python')}",
            *args,
        )
        stdout, _ = await proc.communicate()
        return json.loads(stdout)
