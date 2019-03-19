import pytest
from unittest import mock

from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.cli import cli


@mock.patch("meltano.api.app.start")
def test_ga_tracker(start, project, cli_runner):
    with mock.patch.object(GoogleAnalyticsTracker, "track_meltano_ui") as track:
        cli_runner.invoke(cli, "ui")

        assert track.called
