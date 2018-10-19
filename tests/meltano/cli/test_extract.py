import pytest
from unittest.mock import Mock, MagicMock, patch
from click.testing import CliRunner
from meltano.cli import cli
from meltano.support.runner.singer import SingerRunner


PERFORM_TEST_ARGS = ["extract", "test", "tap-test", "--loader_name", "target-test"]


def test_perform():
    cli_runner = CliRunner()

    result = cli_runner.invoke(cli, ["extract"])
    assert result.exit_code == 2

    # exit cleanly when everything is fine
    with patch.object(SingerRunner, 'perform', return_value=None) as perform:
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 0

    # aborts when there is an exception 
    with patch.object(SingerRunner, 'perform', side_effect=Exception) as perform:
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 1
