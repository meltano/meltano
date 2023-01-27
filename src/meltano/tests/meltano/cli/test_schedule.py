from __future__ import annotations

import mock
import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.utils import iso8601_datetime


class TestCliSchedule:
    @pytest.mark.order(0)
    @pytest.mark.usefixtures("tap", "target")
    @mock.patch(
        "meltano.core.schedule_service.PluginSettingsService.get", autospec=True
    )
    def test_schedule_add(self, get, session, project, cli_runner, schedule_service):
        test_date = "2010-01-01"
        get.return_value = test_date

        # test adding a scheduled elt
        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "add",
                    "elt-schedule-mock",
                    "--extractor",
                    "tap-mock",
                    "--loader",
                    "target-mock",
                    "--interval",
                    "@yearly",
                    "--transform",
                    "run",
                ],
            )

        assert_cli_runner(res)
        schedule = schedule_service.schedules()[0]

        assert schedule.name == "elt-schedule-mock"
        assert schedule.extractor == "tap-mock"
        assert schedule.loader == "target-mock"
        assert schedule.transform == "run"
        assert schedule.interval == "@yearly"  # not anytime soon ;)
        assert schedule.start_date == iso8601_datetime(test_date)

        # test adding a scheduled job
        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "add",
                    "job-schedule-mock",
                    "--job",
                    "mock-job",
                    "--interval",
                    "@yearly",
                ],
            )
        assert res.exit_code == 0

        assert_cli_runner(res)
        schedule = schedule_service.schedules()[1]

        assert schedule.name == "job-schedule-mock"
        assert schedule.job == "mock-job"
        assert schedule.interval == "@yearly"  # not anytime soon ;)

        # test default schedule case where no argument (set, remove, add, etc) is provided
        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "job-schedule-mock",
                    "--job",
                    "mock-job",
                    "--interval",
                    "@yearly",
                ],
            )
        assert res.exit_code == 0

        assert_cli_runner(res)
        schedule = schedule_service.schedules()[1]

        assert schedule.name == "job-schedule-mock"
        assert schedule.job == "mock-job"
        assert schedule.interval == "@yearly"  # not anytime soon ;)

        # verify that you can't use job and elt flags together
        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "add",
                    "job-schedule-mock",
                    "--job",
                    "mock-job",
                    "--extractor",
                    "tap-mock",
                    "--loader",
                    "target-mock",
                    "--interval",
                    "@yearly",
                    "--transform",
                    "run",
                ],
            )

        assert res.exit_code == 1

    @pytest.mark.parametrize("exit_code", [0, 1, 143])
    def test_schedule_run(self, exit_code, cli_runner, elt_schedule, job_schedule):
        process_mock = mock.Mock(returncode=exit_code)
        with mock.patch(
            "meltano.cli.schedule.ScheduleService.run", return_value=process_mock
        ) as run_mock:
            res = cli_runner.invoke(
                cli, ["schedule", "run", elt_schedule.name, "--transform", "run"]
            )
            assert res.exit_code == exit_code
            run_mock.assert_called_once_with(elt_schedule, "--transform", "run")

        with mock.patch(
            "meltano.cli.schedule.ScheduleService.run", return_value=process_mock
        ) as run_mock:
            res = cli_runner.invoke(
                cli, ["schedule", "run", job_schedule.name, "--dry-run"]
            )
            assert res.exit_code == exit_code
            run_mock.assert_called_once_with(job_schedule, "--dry-run")

    def test_schedule_remove(self, cli_runner, job_schedule):
        process_mock = mock.Mock(returncode=0)

        with mock.patch(
            "meltano.cli.schedule.ScheduleService.remove", return_value=process_mock
        ) as remove_mock:
            res = cli_runner.invoke(cli, ["schedule", "remove", job_schedule.name])
            assert res.exit_code == 0
            remove_mock.assert_called_once_with(job_schedule.name)

    def test_schedule_set(
        self, cli_runner, elt_schedule, job_schedule, schedule_service
    ):

        with mock.patch(
            "meltano.cli.schedule.ScheduleService", return_value=schedule_service
        ):
            res = cli_runner.invoke(
                cli, ["schedule", "set", job_schedule.name, "--job", "mock-job-renamed"]
            )
            assert res.exit_code == 0
            assert (
                schedule_service.find_schedule(job_schedule.name).job
                == "mock-job-renamed"
            )

            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "set",
                    elt_schedule.name,
                    "--loader",
                    "mock-target-renamed",
                ],
            )
            assert res.exit_code == 0
            assert (
                schedule_service.find_schedule(elt_schedule.name).loader
                == "mock-target-renamed"
            )

            # interval applies to both and should always work
            res = cli_runner.invoke(
                cli, ["schedule", "set", job_schedule.name, "--interval", "@hourly"]
            )
            assert res.exit_code == 0
            assert (
                schedule_service.find_schedule(job_schedule.name).cron_interval
                == "0 * * * *"
            )

            res = cli_runner.invoke(
                cli, ["schedule", "set", elt_schedule.name, "--interval", "@hourly"]
            )
            assert res.exit_code == 0
            assert (
                schedule_service.find_schedule(elt_schedule.name).cron_interval
                == "0 * * * *"
            )

            # verify that job flags cant be set on elt tasks and vice versa
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "set",
                    job_schedule.name,
                    "--loader",
                    "mock-target-renamed",
                ],
            )
            assert res.exit_code == 1
            assert (
                schedule_service.find_schedule(job_schedule.name).loader
                != "mock-target-renamed"
            )

            res = cli_runner.invoke(
                cli, ["schedule", "set", elt_schedule.name, "--job", "mock-job-renamed"]
            )
            assert res.exit_code == 1
            assert (
                schedule_service.find_schedule(elt_schedule.name).job
                != "mock-job-renamed"
            )
