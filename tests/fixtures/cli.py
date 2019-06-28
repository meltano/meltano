import pytest
import os

from click.testing import CliRunner
from meltano.core.project import Project


@pytest.mark.usefixtures("session")
@pytest.fixture()
def cli_runner(session, pushd):
    # this will make sure we are back at `cwd`
    # after this test is finished
    pushd(os.getcwd())

    yield CliRunner(mix_stderr=False)

    # the CLI activates the meltano project
    # let's make sure we deactivate it after
    Project._default = None
