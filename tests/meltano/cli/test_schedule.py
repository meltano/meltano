import os
from functools import partial
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import iso8601_datetime


class TestCliSchedule:
    @pytest.mark.usefixtures("tap", "target")
    @mock.patch(
        "meltano.core.schedule_service.PluginSettingsService.get", autospec=True
    )
    def test_schedule(self, get, session, project, cli_runner, schedule_service):
        TEST_DATE = "2010-01-01"
        get.return_value = TEST_DATE

        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
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

    @pytest.mark.parametrize("exit_code", [0, 1, 143])
    def test_schedule_run(self, exit_code, cli_runner, schedule):
        process_mock = mock.Mock(returncode=exit_code)
        with mock.patch(
            "meltano.cli.schedule.ScheduleService.run", return_value=process_mock
        ) as run_mock:
            res = cli_runner.invoke(
                cli, ["schedule", "run", schedule.name, "--transform", "run"]
            )
            assert res.exit_code == exit_code

            run_mock.assert_called_once_with(schedule, "--transform", "run")
