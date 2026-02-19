from __future__ import annotations

import os
import platform
import subprocess
import sys
import typing as t
from pathlib import Path
from unittest import mock

import pytest

import meltano
from meltano.core.meltano_invoker import (
    MELTANO_COMMAND,
    MELTANO_PATH_ENV,
    MeltanoInvoker,
)
from meltano.core.tracking.contexts import environment_context

if t.TYPE_CHECKING:
    from meltano.core.project import Project


class TestMeltanoInvoker:
    @pytest.fixture
    def subject(self, project):
        return MeltanoInvoker(project)

    def test_invoke(self, subject: MeltanoInvoker) -> None:
        process = subject.invoke(["--version"], stdout=subprocess.PIPE)
        assert process.returncode == 0
        assert meltano.__version__ in str(process.stdout)

    def test_env(
        self,
        subject: MeltanoInvoker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Process env vars are injected
        monkeypatch.setenv("ENV_VAR_KEY", "ENV_VAR_VALUE_1")
        assert subject._executable_env()["ENV_VAR_KEY"] == "ENV_VAR_VALUE_1"

        # Provided env vars overrides process env vars
        env = subject._executable_env({"ENV_VAR_KEY": "ENV_VAR_VALUE_2"})
        assert env["ENV_VAR_KEY"] == "ENV_VAR_VALUE_2"

        # Environment context UUID from parent process is injected
        assert (
            env["MELTANO_PARENT_CONTEXT_UUID"]
            == environment_context.data["context_uuid"]
        )

    @pytest.mark.xfail(
        reason="Fails on Windows: https://github.com/meltano/meltano/issues/3444",
        condition=platform.system() == "Windows",
        strict=True,
    )
    def test_invoke_executable(
        self,
        subject: MeltanoInvoker,
        project: Project,
    ) -> None:
        process_mock = mock.Mock(returncode=0)
        with mock.patch("subprocess.run", return_value=process_mock) as run_mock:
            subject.invoke(["--version"])

            # Prefer symlink created by Project.activate (when MELTANO_PATH not set)
            symlink_path = project.dirs.run().joinpath("bin")
            assert run_mock.call_args[0][0][0] == str(symlink_path)

            # If a different command is used...
            subject.invoke(["--version"], command="pip")

            # ...the symlink is not relevant and we find the executable next
            # to the `python` executable
            pip_path = Path(os.path.dirname(sys.executable), "pip")  # noqa: PTH120
            assert run_mock.call_args[0][0][0] == str(pip_path)

            # If the `meltano` symlink does not exist...
            symlink_path.unlink()
            subject.invoke(["--version"])

            # we find the executable next to the `python` executable
            meltano_path = Path(os.path.dirname(sys.executable), MELTANO_COMMAND)  # noqa: PTH120
            assert run_mock.call_args[0][0][0] == str(meltano_path)

            # If the executable doesn't exist in either place...
            subject.invoke(["--version"], command="nonexistent")

            # ...we expect it to be in the PATH
            assert run_mock.call_args[0][0][0] == "nonexistent"

    def test_meltano_path_env_set_for_children(
        self,
        subject: MeltanoInvoker,
        project: Project,
    ) -> None:
        """Child processes receive MELTANO_PATH and PATH prefix (issue #6910)."""
        env = subject._executable_env()
        # When we can resolve the meltano executable, MELTANO_PATH is set
        resolved = subject._meltano_executable_path()
        if resolved is not None:
            assert env.get(MELTANO_PATH_ENV) == resolved
            # PATH is prefixed with the directory containing meltano
            assert env["PATH"].startswith(str(Path(resolved).parent))
        else:
            assert MELTANO_PATH_ENV not in env

    def test_meltano_path_env_takes_precedence(
        self,
        subject: MeltanoInvoker,
        project: Project,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When MELTANO_PATH is set in environment, it is used for resolution."""
        custom_path = "/custom/path/to/meltano"
        monkeypatch.setenv(MELTANO_PATH_ENV, custom_path)
        # When MELTANO_PATH is set and the path exists, we use it (e.g. containers)
        with mock.patch.object(Path, "exists", return_value=True):
            assert subject._meltano_executable_path() == custom_path
            env = subject._executable_env()
            assert env[MELTANO_PATH_ENV] == custom_path
            assert env["PATH"].startswith("/custom/path/to")

    def test_meltano_path_env_ignored_when_path_missing(
        self,
        subject: MeltanoInvoker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When MELTANO_PATH is set but path does not exist, we fall back."""
        monkeypatch.setenv(MELTANO_PATH_ENV, "/nonexistent/meltano")
        # Should fall back to symlink or same-dir, not use the missing path
        resolved = subject._meltano_executable_path()
        assert resolved != "/nonexistent/meltano"
