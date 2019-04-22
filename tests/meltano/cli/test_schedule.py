import pytest
import os
from unittest.mock import patch
from functools import partial

from meltano.cli import cli
from meltano.core.tracking import GoogleAnalyticsTracker


class TestCliSchedule:
    def test_schedule(self, project, cli_runner, schedule_service):
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

        project.reload()

        schedule = next(schedule_service.schedules())
        assert schedule.name == "schedule-mock"
        assert schedule.extractor == "tap-mock"
        assert schedule.loader == "target-mock"
        assert schedule.transform == "run"
        assert schedule.interval == "@eon"  # not anytime soon ;)
        assert res.exit_code == 0, res.stdout
