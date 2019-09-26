import pytest
from unittest import mock

from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.cli import cli
from asserts import assert_cli_runner


def test_ui(project, cli_runner):
    # fmt: off
    with mock.patch("meltano.cli.ui.APIWorker.start") as start_api_worker, \
      mock.patch("meltano.cli.ui.MeltanoBackgroundCompiler.start") as start_compiler, \
      mock.patch("meltano.cli.ui.UIAvailableWorker.start") as start_ui_available_worker, \
      mock.patch("meltano.cli.ui.AirflowWorker.start") as start_airflow_worker, \
      mock.patch.object(GoogleAnalyticsTracker, "track_meltano_ui") as track:
        cli_runner.invoke(cli, "ui")

        assert start_api_worker.called
        assert start_ui_available_worker.called
        assert start_compiler.called
        assert start_airflow_worker.called
        assert track.called
    # fmt: on
