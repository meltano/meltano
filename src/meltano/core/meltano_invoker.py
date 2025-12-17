"""Defines MeltanoInvoker."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import typing as t
from pathlib import Path

from meltano.core.project_settings_service import SettingValueStore
from meltano.core.tracking import Tracker

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from meltano.core.project import Project

MELTANO_COMMAND = "meltano"


class MeltanoInvoker:
    """Class used to find and invoke all commands passed to it."""

    def __init__(self, project: Project):
        """Load the class with the project and service settings.

        Args:
            project: Project instance.
        """
        self.project = project
        self.tracker = Tracker(project)

    def invoke(
        self,
        args: Iterable[str],
        command: str = MELTANO_COMMAND,
        env: dict[str, str] | None = None,
        **kwargs: t.Any,
    ) -> subprocess.CompletedProcess[str]:
        """Invoke meltano or other provided command.

        Args:
            args: CLI arguments to pass to the command.
            command: Executable to invoke.
            env: Extra environment variables to use for the subprocess.
            kwargs: Keyword arguments for `subprocess.run`.

        Returns:
            A `CompletedProcess` class object from `subprocess.run`.
        """
        return subprocess.run(
            [self._executable_path(command), *args],
            **kwargs,
            env=self._executable_env(env),
        )

    def _executable_path(self, command):  # noqa: ANN001, ANN202
        if command == MELTANO_COMMAND:
            # This symlink is created by Project.activate
            executable_symlink = self.project.dirs.run().joinpath("bin")
            if executable_symlink.exists():
                return str(executable_symlink)

        executable = Path(
            os.path.dirname(sys.executable),  # noqa: PTH120
            f"{command}.exe" if platform.system() == "Windows" else command,
        )

        # Fall back on expecting command to be in the PATH
        return str(executable) if executable.exists() else command

    def _executable_env(self, env: Mapping[str, str] | None = None) -> dict[str, str]:
        if env is None:
            env = {}
        return {
            # Include env that project settings are evaluated in
            **self.project.settings.env,
            # Include env for settings explicitly overridden using CLI flags
            **self.project.settings.as_env(source=SettingValueStore.CONFIG_OVERRIDE),
            # Include explicitly provided env
            **env,
            # Include telemetry env vars
            **self.tracker.env,
        }
