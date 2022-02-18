import os
import shutil
from copy import copy

import meltano
import pytest
from meltano.cli import cli
from meltano.core.project import PROJECT_READONLY_ENV, Project
from meltano.core.project_settings_service import ProjectSettingsService


class TestCli:
    @pytest.fixture()
    def project(self, test_dir, project_init_service):
        """This fixture returns the non-activated project."""
        project = project_init_service.init(activate=False, add_discovery=True)

        yield project

        Project.deactivate()
        shutil.rmtree(project.root)

    def test_activate_project(self, project, cli_runner, pushd):
        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default is not None
        assert Project._default.root == project.root
        assert Project._default.readonly == False

    def test_activate_project_readonly_env(
        self, project, cli_runner, pushd, monkeypatch
    ):
        monkeypatch.setenv(PROJECT_READONLY_ENV, "true")

        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default.readonly == True

    def test_activate_project_readonly_dotenv(
        self, project, cli_runner, pushd, monkeypatch
    ):
        ProjectSettingsService(project).set("project_readonly", True)

        assert Project._default is None

        pushd(project.root)
        cli_runner.invoke(cli, ["discover"])

        assert Project._default.readonly == True

    def test_version(self, cli_runner):
        cli_version = cli_runner.invoke(cli, ["--version"])

        assert cli_version.output == f"meltano, version {meltano.__version__}\n"
