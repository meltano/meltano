from __future__ import annotations

import typing as t
from unittest import mock

import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.schedule import ELTSchedule, JobSchedule, is_valid_cron
from meltano.core.schedule_service import (
    BadCronError,
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    ScheduleNotFoundError,
)
from meltano.core.utils import NotFound

if t.TYPE_CHECKING:
    from meltano.core.project import Project
    from meltano.core.schedule_service import ScheduleService


@pytest.fixture(scope="session")
def create_elt_schedule():
    def make(name, **kwargs):
        attrs = {
            "extractor": "tap-mock",
            "loader": "target-mock",
            "transform": "run",
            "interval": "@daily",
            "start_date": None,
            "env": {},
        }

        attrs.update(kwargs)
        return ELTSchedule(name=name, **attrs)

    return make


@pytest.fixture(scope="session")
def create_job_schedule():
    def make(name, **kwargs):
        attrs = {
            "job": "job-mock",
            "interval": "@daily",
            "env": {},
        }

        attrs.update(kwargs)
        return JobSchedule(name=name, **attrs)

    return make


@pytest.fixture(scope="class")
def custom_tap(project: Project):
    tap = ProjectPlugin(
        PluginType.EXTRACTORS,
        name="tap-custom",
        namespace="tap_custom",
    )
    try:
        return project.plugins.add_to_file(tap)
    except PluginAlreadyAddedException as err:  # pragma: no cover
        return err.plugin


class TestScheduleService:
    @pytest.fixture
    def subject(self, schedule_service):
        return schedule_service

    @pytest.mark.parametrize(
        "cron",
        (
            pytest.param("@yearly", id="yearly"),
            pytest.param("@annually", id="annually"),
            pytest.param("@monthly", id="monthly"),
            pytest.param("@weekly", id="weekly"),
            pytest.param("@daily", id="daily"),
            pytest.param("@midnight", id="midnight"),
            pytest.param("@hourly", id="hourly"),
            pytest.param("0 0 1 1 0", id="New Year's Day at midnight"),
            pytest.param("30 14 * * 1-5", id="2:30 PM weekdays"),
            pytest.param("0 22 * * 7", id="10 PM every Sunday"),
            pytest.param("0 0 * jan-jun *", id="every day in January through June"),
            pytest.param("0 0 * dec mon", id="every Monday in December"),
            pytest.param("0 0 ? * *", id="special character ? for day field"),
            pytest.param("0 0 * * ?", id="special character ? for dow field"),
            pytest.param("0 0 L * *", id="last day of month"),
            pytest.param("0 0 3,13,23 * *", id="3rd, 13th, and 23rd day of month"),
            pytest.param("0 0 20-L * *", id="20th through last day of month"),
            pytest.param("0 0 * * 5-7", id="every Friday through Sunday"),
            pytest.param("0 0 * * fri-tue", id="every Friday through Tuesday"),
            pytest.param("0 0 */3 * *", id="every 3 hours"),
            pytest.param("0 0 6-14/2 * *", id="every 2 hours from 6 AM to 2 PM"),
        ),
    )
    def test_valid_cron(self, cron: str):
        assert is_valid_cron(cron)

    @pytest.mark.parametrize(
        "cron",
        (
            pytest.param("0 0 /3 * *", id="empty base"),
            pytest.param("0 0 */x * *", id="invalid step"),
            pytest.param("0 0 * ? *", id="special character ? in other places"),
            pytest.param("0 a * * *", id="invalid hour part"),
            pytest.param("0 0 a-31 * *", id="invalid range parts"),
            pytest.param("0 0 -31 * *", id="invalid range parts"),
            pytest.param("* * * ene-dic *", id="unknown month aliases"),
            pytest.param("0 0 * * dec dom", id="unknown day of week aliases"),
            pytest.param("0 0 1 1 0 0", id="6-field format"),
            pytest.param("0 0 1 1 0 0 2025", id="7-field format"),
        ),
    )
    def test_invalid_cron(self, cron: str):
        assert not is_valid_cron(cron)

    @pytest.mark.order(0)
    def test_add_schedules(
        self,
        subject,
        create_elt_schedule,
        create_job_schedule,
    ) -> None:
        intervals = [
            "@once",
            "@manual",
            "@none",
            "@hourly",
            "@daily",
            "@weekly",
            "@monthly",
            "@yearly",
        ]

        job_schedules = [
            create_job_schedule(f"job_schedule_{interval[1:]}", interval=interval)
            for interval in intervals
        ]
        elt_schedules = [
            create_elt_schedule(f"elt_schedule_{interval[1:]}", interval=interval)
            for interval in intervals
        ]

        all_schedules = job_schedules + elt_schedules

        for schedule in all_schedules:
            subject.add_schedule(schedule)

        assert subject.schedules() == all_schedules

        # but name must be unique
        with pytest.raises(ScheduleAlreadyExistsError):
            subject.add_schedule(all_schedules[0])

        with pytest.raises(BadCronError) as excinfo:
            subject.add_schedule(create_elt_schedule("bad-cron", interval="bad_cron"))

        assert "bad_cron" in str(excinfo.value)
        assert excinfo.value.reason == "Invalid Cron expression or alias: 'bad_cron'"
        assert excinfo.value.instruction == "Please use a valid cron expression"

    def test_remove_schedule(self, subject) -> None:
        schedules = list(subject.schedules())
        schedules_count = len(schedules)

        idx = 3
        target_schedule = schedules[idx]
        target_name = target_schedule.name

        subject.remove_schedule(target_name)

        # make sure one has been removed
        schedules = list(subject.schedules())
        assert len(schedules) == schedules_count - 1
        assert target_schedule not in schedules

        # schedule name must exist to be removed
        with pytest.raises(ScheduleDoesNotExistError):
            subject.remove_schedule(target_name)

    def test_schedule_update(self, subject) -> None:
        schedule = subject.schedules()[0]

        yearly_intervals = sum(sbj.interval == "@yearly" for sbj in subject.schedules())

        schedule.interval = "@yearly"
        subject.update_schedule(schedule)

        # there should be one more schedule with the "@yearly" interval after set
        assert (
            sum(sbj.interval == "@yearly" for sbj in subject.schedules())
            == yearly_intervals + 1
        )

        # it should be the first element
        assert subject.schedules()[0].interval == "@yearly"

        # it should be a copy of the original element
        assert schedule is not subject.schedules()[0]

        # it must exists
        schedule.name = "llamasareverynice"
        with pytest.raises(ScheduleDoesNotExistError):
            subject.update_schedule(schedule)

    def test_run_elt_schedule(self, subject, tap, target) -> None:
        schedule = subject.add_elt(
            "tap-to-target",
            tap.name,
            target.name,
            "skip",
            "@daily",
            TAP_MOCK_TEST="overridden",
        )

        # It fails because tap and target are not actually installed
        process = subject.run(schedule)
        assert process.returncode == 1

        process_mock = mock.Mock(returncode=0)
        with mock.patch(
            "meltano.core.schedule_service.MeltanoInvoker.invoke",
            return_value=process_mock,
        ) as invoke_mock:
            process = subject.run(
                schedule,
                "--dump=config",
                env={"TAP_MOCK_SECURE": "overridden"},
            )
            assert process.returncode == 0

            invoke_mock.assert_called_once_with(
                [
                    "elt",
                    tap.name,
                    target.name,
                    f"--transform={schedule.transform}",
                    f"--state-id={schedule.name}",
                    "--dump=config",
                ],
                env={"TAP_MOCK_TEST": "overridden", "TAP_MOCK_SECURE": "overridden"},
            )

    @pytest.mark.usefixtures("session", "tap", "target")
    def test_run_job_schedule(self, subject) -> None:
        schedule = subject.add(
            "mock-job-schedule",
            "mock-job",
            "@daily",
            MOCK_ENV_FROM_SCHED="env_var_value_from_schedule_def",
        )

        # It fails because mock-job is not a valid job
        assert subject.run(schedule).returncode == 1

        process_mock = mock.Mock(returncode=0)
        with mock.patch(
            "meltano.core.schedule_service.MeltanoInvoker.invoke",
            return_value=process_mock,
        ) as invoke_mock:
            process = subject.run(
                schedule,
                "--dry-run",
                env={"MOCK_ENV_ENTRY": "athing"},
            )
            assert process.returncode == 0

            invoke_mock.assert_called_once_with(
                [
                    "run",
                    "--dry-run",
                    schedule.job,
                ],
                env={
                    "MOCK_ENV_ENTRY": "athing",
                    "MOCK_ENV_FROM_SCHED": "env_var_value_from_schedule_def",
                },
            )

    def test_find_namespace_schedule(self, subject, tap, create_elt_schedule) -> None:
        schedule = create_elt_schedule(tap.name)
        subject.add_schedule(schedule)
        found_schedule = subject.find_namespace_schedule(tap.namespace)
        assert found_schedule.extractor == tap.name

    @pytest.mark.usefixtures("create_elt_schedule")
    def test_find_namespace_schedule_custom_extractor(
        self,
        subject: ScheduleService,
        custom_tap,
    ) -> None:
        schedule = ELTSchedule(
            name="tap-custom",
            extractor="tap-custom",
            loader="target-mock",
            transform="skip",
            interval="@daily",
        )
        subject.add_schedule(schedule)
        found_schedule = subject.find_namespace_schedule(custom_tap.namespace)
        assert isinstance(found_schedule, ELTSchedule)
        assert found_schedule.extractor == custom_tap.name

    def test_find_namespace_schedule_not_found(self, subject) -> None:
        with pytest.raises(ScheduleNotFoundError):
            subject.find_namespace_schedule("no-such-namespace")

    def test_find_schedule_not_found(self, subject) -> None:
        with pytest.raises(NotFound):
            subject.find_schedule("no-such-schedule")
