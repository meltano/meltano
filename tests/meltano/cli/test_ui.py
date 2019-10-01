import pytest
from unittest import mock

from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.cli import cli
from asserts import assert_cli_runner


@mock.patch("meltano.cli.ui.start")
def test_ga_tracker(start, project, cli_runner):
    with mock.patch.object(GoogleAnalyticsTracker, "track_meltano_ui") as track:
        res = cli_runner.invoke(cli, "ui")

        assert track.called

    assert start.called

    assert_cli_runner(res)
