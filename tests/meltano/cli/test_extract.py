import os
from unittest.mock import patch
from functools import partial
from click.testing import CliRunner

from meltano.cli import cli
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner


PERFORM_TEST_ARGS = [
    "elt",
    "test",
    "--extractor",
    "tap-test",
    "--loader",
    "target-test",
]


def test_elt(request, project):
    # popd
    popd = partial(os.chdir, os.getcwd())
    request.addfinalizer(popd)

    # move into the project
    os.chdir(project.root)

    cli_runner = CliRunner()

    result = cli_runner.invoke(cli, ["elt"])
    assert result.exit_code == 2

    # exit cleanly when everything is fine
    with patch.object(SingerRunner, "perform", return_value=None), patch.object(
        DbtRunner, "perform", return_value=None
    ):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 0

    # aborts when there is an exception
    with patch.object(SingerRunner, "perform", side_effect=Exception):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 1

    with patch.object(SingerRunner, "perform", side_effect=Exception):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 1
