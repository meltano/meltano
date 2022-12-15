"""Defines MeltanoInvoker."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from meltano.core.project import Project
from meltano.core.project_settings_service import (
    ProjectSettingsService,
    SettingValueStore,
)
from meltano.core.tracking import Tracker

MELTANO_COMMAND = "meltano"


class MeltanoInvoker:
    """Class used to find and invoke all commands passed to it."""

    def __init__(
        self, project: Project, settings_service: ProjectSettingsService | None = None
    ):
        """
        Load the class with the project and service settings.

        Args:
            project: Project class
            settings_service: ProjectSettingsService Class blank
        """
        self.project = project
        self.tracker = Tracker(project)
        self.settings_service = settings_service or ProjectSettingsService(project)

    def invoke(self, args, command=MELTANO_COMMAND, env=None, **kwargs):
        """
        Invoke meltano or other provided command.

        Args:
            args: list.
            command: string containing command to invoke.
            env: dictionary.
            kwargs: dictionary.

        Returns:
            A CompletedProcess class object from subprocess.run().
        """
        return subprocess.run(
            [self._executable_path(command), *args],
            **kwargs,
            env=self._executable_env(env),
        )

    def _executable_path(self, command):
        if command == MELTANO_COMMAND:
            # This symlink is created by Project.activate
            executable_symlink = self.project.run_dir().joinpath("bin")
            if executable_symlink.exists():
                return str(executable_symlink)

        executable = Path(
            os.path.dirname(sys.executable),
            f"{command}.exe" if platform.system() == "Windows" else command,
        )

        # Fall back on expecting command to be in the PATH
        return str(executable) if executable.exists() else command

    def _executable_env(self, env: Mapping[str, str] | None = None) -> dict[str, str]:
        if env is None:
            env = {}
        return {
            # Include env that project settings are evaluated in
            **self.settings_service.env,
            # Include env for settings explicitly overridden using CLI flags
            **self.settings_service.as_env(source=SettingValueStore.CONFIG_OVERRIDE),
            # Include explicitly provided env
            **env,
            # Include telemetry env vars
            **self.tracker.env,
        }
