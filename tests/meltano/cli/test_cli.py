import pytest
import os
from copy import copy
from click.testing import CliRunner

from meltano.cli import cli


def test_activate_project(project_init_service, test_dir):
    # create a project and `cd` into it
    project = project_init_service.init()
    os.chdir(project.root)

    # let's overwrite the `.env` to add a sentinel value
    with project.root.joinpath(".env").open("w") as env:
        env.write("CLI_TEST_ACTIVATE_PROJECT=1")

    # run a cli command - that should activate the project
    runner = CliRunner()
    runner.invoke(cli, ["install"])

    assert os.getenv("CLI_TEST_ACTIVATE_PROJECT") == "1"
