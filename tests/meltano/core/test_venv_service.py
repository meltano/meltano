import pytest
import os

from meltano.core.venv_service import VenvService


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
