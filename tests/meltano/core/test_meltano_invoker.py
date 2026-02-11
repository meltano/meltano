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
from meltano.core.meltano_invoker import MELTANO_COMMAND, MeltanoInvoker
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

            # Preferally, we use the symlink created by Project.activate
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
