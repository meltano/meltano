import pytest
import os
import sys
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
