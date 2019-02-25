import pytest
import os
import shutil
from copy import copy

import meltano
from meltano.cli import cli


@pytest.fixture
def project(test_dir, project_init_service):
    """This fixture returns the non-activated project."""
    project = project_init_service.init()

    yield project

    os.chdir(test_dir)
    shutil.rmtree(project.root)


def test_activate_project(project, cli_runner, pushd):
    # `cd` into a project
    pushd(project.root)

    # let's overwrite the `.env` to add a sentinel value
    with project.root.joinpath(".env").open("w") as env:
        env.write("CLI_TEST_ACTIVATE_PROJECT=1")

    # run any cli command - that should activate the project
    cli_runner.invoke(cli, ["install"])

    assert os.getenv("CLI_TEST_ACTIVATE_PROJECT") == "1"


def test_version(cli_runner):
    cli_version = cli_runner.invoke(cli, ["--version"])

    assert cli_version.output == f"meltano, version {meltano.__version__}\n"
