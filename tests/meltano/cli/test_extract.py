import os
from unittest.mock import patch
from functools import partial
from click.testing import CliRunner

from meltano.cli import cli
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.dbt_service import DbtService
from meltano.core.tracking import GoogleAnalyticsTracker


PERFORM_TEST_ARGS = ["elt", "tap-test", "target-test"]


def mock_install_missing_plugins(project, extractor, loader, transform):
    pass


def test_elt(request, project):
    cli_runner = CliRunner()

    result = cli_runner.invoke(cli, ["elt"])
    assert result.exit_code == 2

    # exit cleanly when everything is fine
    with patch.object(SingerRunner, "run", return_value=None), patch.object(
        GoogleAnalyticsTracker, "track_data", return_value=None
    ), patch(
        "meltano.cli.elt.install_missing_plugins",
        side_effect=mock_install_missing_plugins,
    ):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 0

    # aborts when there is an exception
    with patch(
        "meltano.cli.elt.install_missing_plugins",
        side_effect=mock_install_missing_plugins,
    ):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 1

    with patch.object(SingerRunner, "run", side_effect=Exception):
        result = cli_runner.invoke(cli, PERFORM_TEST_ARGS)
        assert result.exit_code == 1
