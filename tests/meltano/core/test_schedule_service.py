from __future__ import annotations

import platform
from datetime import datetime

import mock
import pytest

from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.schedule_service import (
    BadCronError,
    Schedule,
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    ScheduleNotFoundError,
    SettingMissingError,
)


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
        return Schedule(name=name, **attrs)

    return make


@pytest.fixture(scope="session")
def create_job_schedule():
    def make(name, **kwargs):
        attrs = {
            "job": "job-mock",
            "interval": "@daily",
            "start_date": None,
            "env": {},
        }

        attrs.update(kwargs)
        return Schedule(name=name, **attrs)

    return make


@pytest.fixture(scope="class")
def custom_tap(project_add_service):
    tap = ProjectPlugin(
        PluginType.EXTRACTORS, name="tap-custom", namespace="tap_custom"
    )
    try:
        return project_add_service.add_plugin(tap)
    except PluginAlreadyAddedException as err:
        return err.plugin


class TestScheduleService:
    @pytest.fixture()
    def subject(self, schedule_service):
        return schedule_service

    @pytest.mark.order(0)
    def test_add_schedules(self, subject, create_elt_schedule, create_job_schedule):
        count = 5

        job_schedules = [
            create_job_schedule(f"job_schedule_{idx}") for idx in range(count)
        ]
        elt_schedules = [
            create_elt_schedule(f"elt_schedule_{idx}") for idx in range(count)
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

    def test_remove_schedule(self, subject):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

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

    def test_schedule_update(self, subject):
        schedule = subject.schedules()[0]

        schedule.interval = "@yearly"
        subject.update_schedule(schedule)

        # there should be only 1 element with the set interval
        assert sum(sbj.interval == "@yearly" for sbj in subject.schedules()) == 1

        # it should be the first element
        assert subject.schedules()[0].interval == "@yearly"

        # it should be a copy of the original element
        assert schedule is not subject.schedules()[0]

        # it must exists
        with pytest.raises(ScheduleDoesNotExistError):
            schedule.name = "llamasareverynice"
            subject.update_schedule(schedule)

    def test_schedule_start_date(
        self, subject, session, tap, target, plugin_settings_service_factory
    ):
        # curry the `add_elt` method to remove some arguments
        add_elt = lambda name, start_date: subject.add_elt(  # noqa: E731
            session, name, tap.name, target.name, "run", "@daily", start_date=start_date
        )

        mock_date = datetime(2002, 1, 1)  # noqa: WPS432

        # when a start_date is set, the schedule should use it
        schedule = add_elt("with_start_date", mock_date)
        assert schedule.start_date == mock_date

        # or use the start_date in the extractor configuration
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set("start_date", mock_date, session=session)
        schedule = add_elt("with_default_start_date", None)
        assert schedule.start_date == mock_date

        # or default to `utcnow()` if the plugin exposes no config
        with mock.patch(
            "meltano.core.schedule_service.PluginSettingsService.get",
            side_effect=SettingMissingError("start_date"),
        ):
            schedule = add_elt("with_no_start_date", None)
            assert schedule.start_date

    def test_run_elt_schedule(self, subject, session, tap, target):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

        schedule = subject.add_elt(
            session,
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
                schedule, "--dump=config", env={"TAP_MOCK_SECURE": "overridden"}
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

    def test_run_job_schedule(self, subject, session, tap, target):
        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/3444"
            )

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
                schedule, "--dry-run", env={"MOCK_ENV_ENTRY": "athing"}
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

    def test_find_namespace_schedule(
        self, subject, tap, create_elt_schedule, project_plugins_service
    ):
        schedule = create_elt_schedule(tap.name)
        subject.add_schedule(schedule)
        with mock.patch(
            "meltano.core.project_plugins_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            found_schedule = subject.find_namespace_schedule(tap.namespace)
            assert found_schedule.extractor == tap.name

    def test_find_namespace_schedule_custom_extractor(
        self, subject, create_elt_schedule, custom_tap, project_plugins_service
    ):
        schedule = Schedule(name="tap-custom", extractor="tap-custom")
        subject.add_schedule(schedule)
        with mock.patch(
            "meltano.core.project_plugins_service.ProjectPluginsService",
            return_value=project_plugins_service,
        ):
            found_schedule = subject.find_namespace_schedule(custom_tap.namespace)
            assert found_schedule.extractor == custom_tap.name

    def test_find_namespace_schedule_not_found(self, subject):
        with pytest.raises(ScheduleNotFoundError):
            subject.find_namespace_schedule("no-such-namespace")
