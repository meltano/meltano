import pytest
import os
import shutil
from copy import copy

import meltano
from meltano.cli import cli
from meltano.core.project import Project


class TestCli:
    @pytest.fixture(scope="class")
    def project(self, test_dir, project_init_service):
        """This fixture returns the non-activated project."""
        project = project_init_service.init(activate=False, add_discovery=True)

        yield project

        shutil.rmtree(project.root)

    def test_activate_project(self, project, cli_runner, pushd):
        assert Project._default is None

        # `cd` into a project
        pushd(project.root)

        # run any cli command - that should activate the project
        cli_runner.invoke(cli, ["discover"])

        assert Project._default is not None
        assert Project._default.root == project.root

    def test_version(self, cli_runner):
        cli_version = cli_runner.invoke(cli, ["--version"])

        assert cli_version.output == f"meltano, version {meltano.__version__}\n"
