import pytest
import os
from unittest import mock
from functools import partial

from meltano.cli import cli
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import iso8601_datetime
from asserts import assert_cli_runner


class TestCliSchedule:
    @pytest.mark.usefixtures("tap", "target")
    @mock.patch(
        "meltano.core.schedule_service.PluginSettingsService.get", autospec=True
    )
    def test_schedule(self, get, session, project, cli_runner, schedule_service):
        TEST_DATE = "2010-01-01"
        get.return_value = TEST_DATE

        res = cli_runner.invoke(
            cli,
            [
                "schedule",
                "schedule-mock",
                "tap-mock",
                "target-mock",
                "@eon",
                "--transform",
                "run",
            ],
        )

        assert_cli_runner(res)
        schedule = schedule_service.schedules()[0]

        assert schedule.name == "schedule-mock"
        assert schedule.extractor == "tap-mock"
        assert schedule.loader == "target-mock"
        assert schedule.transform == "run"
        assert schedule.interval == "@eon"  # not anytime soon ;)
        assert schedule.start_date == iso8601_datetime(TEST_DATE)
