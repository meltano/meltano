import pytest
import os
import sys
import subprocess
from unittest import mock

from meltano.core.venv_service import VenvService, VirtualEnv


class TestVenvService:
    @pytest.fixture
    def subject(self, project):
        return VenvService(project)

    def test_create(self, project, subject):
        subject.create(name="name", namespace="namespace")
        venv_dir = subject.project.venvs_dir("namespace", "name")

        # ensure the venv is created
        assert venv_dir.exists()

        # ensure that the binary is python3
        assert os.path.samefile(
            venv_dir.joinpath("bin/python"), venv_dir.joinpath("bin/python3")
        )

        # ensure that pip is the latest version
        run = subprocess.run(
            [venv_dir.joinpath("bin/python"), "-m", "pip", "list", "--outdated"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for line in str(run.stdout).splitlines():
            assert line.startswith("pip ") == False


class TestVirtualEnv:
    @pytest.mark.parametrize("system", ["Linux", "Darwin", "Windows"])
    def test_cross_platform(self, system, project):
        python = f"python{sys.version[:3]}"

        with mock.patch("platform.system", return_value=system):
            subject = VirtualEnv(project.venvs_dir("pytest", "pytest"))
            assert subject._specs == VirtualEnv.PLATFORM_SPECS[system]

    def test_unknown_platform(self):
        # fmt: off
        with mock.patch("platform.system", return_value="commodore64"), \
          pytest.raises(Exception):
        # fmt: on
            subject = VirtualEnv(project.venvs_dir("pytest", "pytest"))
            assert str(ex) == "Platform commodore64 is not supported."
