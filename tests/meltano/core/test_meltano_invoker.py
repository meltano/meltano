import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

import meltano
from meltano.core.meltano_invoker import MELTANO_COMMAND, MeltanoInvoker


class TestMeltanoInvoker:
    @pytest.fixture
    def subject(self, project):
        return MeltanoInvoker(project)

    def test_invoke(self, subject):
        process = subject.invoke(["--version"], stdout=subprocess.PIPE)
        assert process.returncode == 0
        assert meltano.__version__ in str(process.stdout)  # noqa: WPS609

    def test_invoke_executable(self, subject, project):
        process_mock = mock.Mock(returncode=0)
        with mock.patch("subprocess.run", return_value=process_mock) as run_mock:
            subject.invoke(["--version"])

            # Preferally, we use the symlink created by Project.activate
            symlink_path = project.run_dir().joinpath("bin")
            assert run_mock.call_args[0][0][0] == str(symlink_path)

            # If a different command is used...
            subject.invoke(["--version"], command="gunicorn")

            # ...the symlink is not relevant and we find the executable next to the `python` executable
            gunicorn_path = Path(os.path.dirname(sys.executable), "gunicorn")
            assert run_mock.call_args[0][0][0] == str(gunicorn_path)

            # If the `meltano` symlink does not exist...
            symlink_path.unlink()
            subject.invoke(["--version"])

            # we find the executable next to the `python` executable
            meltano_path = Path(os.path.dirname(sys.executable), MELTANO_COMMAND)
            assert run_mock.call_args[0][0][0] == str(meltano_path)

            # If the executable doesn't exist in either place...
            subject.invoke(["--version"], command="nonexistent")

            # ...we expect it to be in the PATH
            assert run_mock.call_args[0][0][0] == "nonexistent"
