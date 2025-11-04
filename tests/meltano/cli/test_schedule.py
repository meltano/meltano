from __future__ import annotations

import json
import typing as t
from unittest import mock

import pytest

from asserts import assert_cli_runner
from meltano.cli import cli
from meltano.core.schedule import ELTSchedule, JobSchedule
from meltano.core.schedule_service import BadCronError
from meltano.core.task_sets import TaskSets

if t.TYPE_CHECKING:
    from fixtures.cli import MeltanoCliRunner
    from meltano.core.schedule_service import ScheduleService


class TestCliSchedule:
    @pytest.mark.order(0)
    @pytest.mark.usefixtures("project", "session", "tap", "target")
    def test_schedule_add(
        self,
        cli_runner: MeltanoCliRunner,
        schedule_service: ScheduleService,
    ) -> None:
        # test adding a scheduled elt
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
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

        assert isinstance(schedule, ELTSchedule)
        assert schedule.name == "elt-schedule-mock"
        assert schedule.extractor == "tap-mock"
        assert schedule.loader == "target-mock"
        assert schedule.transform == "run"
        assert schedule.interval == "@yearly"  # not anytime soon ;)

        # test adding a scheduled job
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
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

        assert isinstance(schedule, JobSchedule)
        assert schedule.name == "job-schedule-mock"
        assert schedule.job == "mock-job"
        assert schedule.interval == "@yearly"  # not anytime soon ;)

        # Test default schedule case where no argument (set, remove, add, etc)
        # is provided
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
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

        assert isinstance(schedule, JobSchedule)
        assert schedule.name == "job-schedule-mock"
        assert schedule.job == "mock-job"
        assert schedule.interval == "@yearly"  # not anytime soon ;)

        # verify that you can't use job and elt flags together
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
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

        # Can't omit --extractor/--loader for an EL(T) schedule
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
        ):
            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "add",
                    "elt-schedule-mock",
                    "--interval=@hourly",
                    "--loader=target-mock",
                ],
            )
            assert res.exit_code == 2
            assert "Missing --extractor" in res.stderr

            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "add",
                    "elt-schedule-mock",
                    "--interval=@hourly",
                    "--extractor=tap-mock",
                ],
            )
            assert res.exit_code == 2
            assert "Missing --loader" in res.stderr

    @pytest.mark.parametrize("exit_code", (0, 1, 143))
    def test_schedule_run(
        self,
        exit_code: int,
        cli_runner: MeltanoCliRunner,
        elt_schedule: ELTSchedule,
        job_schedule: JobSchedule,
    ) -> None:
        process_mock = mock.Mock(returncode=exit_code)
        with mock.patch(
            "meltano.cli.schedule.ScheduleService.run",
            return_value=process_mock,
        ) as run_mock:
            res = cli_runner.invoke(
                cli,
                ["schedule", "run", elt_schedule.name, "--transform", "run"],
            )
            assert res.exit_code == exit_code
            run_mock.assert_called_once_with(elt_schedule, "--transform", "run")

        with mock.patch(
            "meltano.cli.schedule.ScheduleService.run",
            return_value=process_mock,
        ) as run_mock:
            res = cli_runner.invoke(
                cli,
                ["schedule", "run", job_schedule.name, "--dry-run"],
            )
            assert res.exit_code == exit_code
            run_mock.assert_called_once_with(job_schedule, "--dry-run")

    def test_schedule_remove(
        self,
        cli_runner: MeltanoCliRunner,
        job_schedule: JobSchedule,
    ) -> None:
        process_mock = mock.Mock(returncode=0)

        with mock.patch(
            "meltano.cli.schedule.ScheduleService.remove_schedule",
            return_value=process_mock,
        ) as remove_mock:
            res = cli_runner.invoke(cli, ["schedule", "remove", job_schedule.name])
            assert res.exit_code == 0
            remove_mock.assert_called_once_with(job_schedule.name)

    def test_schedule_set(
        self,
        cli_runner: MeltanoCliRunner,
        elt_schedule: ELTSchedule,
        job_schedule: JobSchedule,
        schedule_service: ScheduleService,
    ) -> None:
        with mock.patch(
            "meltano.cli.schedule.ScheduleService",
            return_value=schedule_service,
        ):
            res = cli_runner.invoke(
                cli,
                ["schedule", "set", job_schedule.name, "--job", "mock-job-renamed"],
            )
            assert res.exit_code == 0
            schedule = schedule_service.find_schedule(job_schedule.name)
            assert isinstance(schedule, JobSchedule)
            assert schedule.job == "mock-job-renamed"

            res = cli_runner.invoke(
                cli,
                [
                    "schedule",
                    "set",
                    elt_schedule.name,
                    "--extractor",
                    "mock-tap-renamed",
                ],
            )
            assert res.exit_code == 0
            schedule = schedule_service.find_schedule(elt_schedule.name)
            assert isinstance(schedule, ELTSchedule)
            assert schedule.extractor == "mock-tap-renamed"

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
            schedule = schedule_service.find_schedule(elt_schedule.name)
            assert isinstance(schedule, ELTSchedule)
            assert schedule.loader == "mock-target-renamed"

            # interval applies to both and should always work
            res = cli_runner.invoke(
                cli,
                ["schedule", "set", job_schedule.name, "--interval", "@hourly"],
            )
            assert res.exit_code == 0
            assert (
                schedule_service.find_schedule(job_schedule.name).cron_interval
                == "0 * * * *"
            )

            # Should raise exception for invalid cron interval
            res = cli_runner.invoke(
                cli,
                ["schedule", "set", elt_schedule.name, "--interval", "@hourl"],
            )
            assert res.exit_code != 0
            assert isinstance(res.exception, BadCronError)

            res = cli_runner.invoke(
                cli,
                ["schedule", "set", elt_schedule.name, "--interval", "@hourly"],
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
            assert "Cannot mix --job" in res.stderr
            assert isinstance(
                schedule_service.find_schedule(job_schedule.name),
                JobSchedule,
            )

            res = cli_runner.invoke(
                cli,
                ["schedule", "set", elt_schedule.name, "--job", "mock-job-renamed"],
            )
            assert res.exit_code == 1
            assert "Cannot mix --job" in res.stderr
            assert isinstance(
                schedule_service.find_schedule(elt_schedule.name),
                ELTSchedule,
            )

    def test_schedule_list(
        self,
        cli_runner: MeltanoCliRunner,
        elt_schedule: ELTSchedule,
        job_schedule: JobSchedule,
        schedule_service: ScheduleService,
    ) -> None:
        class DummyTaskSetsService:
            def get(self, name: str) -> TaskSets:
                return TaskSets(name, ["task1", "task2"])

        with (
            mock.patch(
                "meltano.cli.schedule.ScheduleService",
                return_value=schedule_service,
            ),
            mock.patch(
                "meltano.cli.schedule.TaskSetsService",
                return_value=DummyTaskSetsService(),
            ),
        ):
            res = cli_runner.invoke(cli, ["schedule", "list"])
            assert res.exit_code == 0
            assert f"elt {elt_schedule.name}" in res.stdout
            assert f"job {job_schedule.name}" in res.stdout

            res = cli_runner.invoke(cli, ["schedule", "list", "--format", "json"])
            assert res.exit_code == 0
            schedules = json.loads(res.stdout)["schedules"]
            assert schedules["elt"][0]["name"] == elt_schedule.name
            assert schedules["job"][0]["name"] == job_schedule.name
