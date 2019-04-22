import pytest
import os
from unittest.mock import patch
from functools import partial

from meltano.cli import cli
from meltano.core.runner.singer import SingerRunner
from meltano.core.runner.dbt import DbtRunner
from meltano.core.dbt_service import DbtService
from meltano.core.tracking import GoogleAnalyticsTracker


PERFORM_TEST_ARGS = ["elt", "tap-test", "target-test"]
PERFORM_ONLY_TRANSFORM_ARGS = ["elt", "tap-test", "target-test", "--transform", "only"]


def mock_install_missing_plugins(project, extractor, loader, transform):
    pass


@pytest.mark.backend("sqlite")
def test_elt(cli_runner, monkeypatch, project):
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

    # exit cleanly when `meltano elt ... --transform only` runs for
    # a tap with no default transforms
    with patch.object(SingerRunner, "run", return_value=None), patch.object(
        GoogleAnalyticsTracker, "track_data", return_value=None
    ), patch("meltano.cli.elt.add_plugin", return_value=None), patch.object(
        DbtRunner, "run", return_value=None
    ):
        result = cli_runner.invoke(cli, PERFORM_ONLY_TRANSFORM_ARGS)
        assert result.exit_code == 0
