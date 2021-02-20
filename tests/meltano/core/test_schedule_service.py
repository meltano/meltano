from datetime import datetime
from unittest import mock

import pytest
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.schedule_service import (
    Schedule,
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    ScheduleService,
    SettingMissingError,
)


@pytest.fixture(scope="session")
def create_schedule():
    def make(name, **kwargs):
        attrs = dict(
            extractor="tap-mock",
            loader="target-mock",
            transform="run",
            interval="@daily",
            start_date=None,
            env={},
        )

        attrs.update(kwargs)
        return Schedule(name=name, **attrs)

    return make


@pytest.fixture(scope="class")
def custom_tap(project_add_service):
    EXPECTED = {"test": "custom", "start_date": None, "secure": None}
    tap = ProjectPlugin(
        PluginType.EXTRACTORS,
        name="tap-custom",
        namespace="tap_custom",
        config=EXPECTED,
    )
    try:
        return project_add_service.add_plugin(tap)
    except PluginAlreadyAddedException as err:
        return err.plugin


class TestScheduleService:
    @pytest.fixture()
    def subject(self, schedule_service):
        return schedule_service

    def test_add_schedule(self, subject, create_schedule):
        COUNT = 10

        schedules = [create_schedule(f"schedule_{i}") for i in range(COUNT)]
        for schedule in schedules:
            subject.add_schedule(schedule)

        assert subject.schedules() == schedules

        # but name must be unique
        with pytest.raises(ScheduleAlreadyExistsError):
            subject.add_schedule(schedules[0])

    def test_remove_schedule(self, subject):
        schedules = list(subject.schedules())
        schedules_count = len(schedules)

        idx = 3
        target_schedule = schedules[idx]
        target_name = f"schedule_{idx}"

        assert target_schedule.name == target_name

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

        schedule.interval = "@pytest"
        subject.update_schedule(schedule)

        # there should be only 1 element with the set interval
        assert sum(map(lambda s: s.interval == "@pytest", subject.schedules())) == 1

        # it should be the first element
        assert subject.schedules()[0].interval == "@pytest"

        # it should be a copy of the original element
        assert schedule is not subject.schedules()[0]

        # it must exists
        with pytest.raises(ScheduleDoesNotExistError):
            schedule.name = "llamasareverynice"
            subject.update_schedule(schedule)

    def test_schedule_start_date(
        self, subject, session, tap, target, plugin_settings_service_factory
    ):
        # curry the `add` method to remove some arguments
        add = lambda name, start_date: subject.add(
            session, name, tap.name, target.name, "run", "@daily", start_date=start_date
        )

        # when a start_date is set, the schedule should use it
        schedule = add("with_start_date", datetime(2001, 1, 1))
        assert schedule.start_date == datetime(2001, 1, 1)

        # or use the start_date in the extractor configuration
        plugin_settings_service = plugin_settings_service_factory(tap)
        plugin_settings_service.set("start_date", datetime(2002, 1, 1), session=session)
        schedule = add("with_default_start_date", None)
        assert schedule.start_date == datetime(2002, 1, 1)

        # or default to `utcnow()` if the plugin exposes no config
        with mock.patch(
            "meltano.core.schedule_service.PluginSettingsService.get",
            side_effect=SettingMissingError("start_date"),
        ):
            schedule = add("with_no_start_date", None)
            assert schedule.start_date

    def test_run(self, subject, session, tap, target):
        schedule = subject.add(
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
                    f"--job_id={schedule.name}",
                    "--dump=config",
                ],
                env={"TAP_MOCK_TEST": "overridden", "TAP_MOCK_SECURE": "overridden"},
            )

    def test_find_namespace_schedule(self, subject, tap, create_schedule, project_plugins_service):
        schedule = create_schedule(tap.name)
        subject.add_schedule(schedule)
        found_schedule = [sched for sched in list(subject.schedules())][0]
        with mock.patch(
            "meltano.core.project_plugins_service.ProjectPluginsService",
            return_value=project_plugins_service
        ):
            extractor = project_plugins_service.find_plugin_by_namespace(PluginType.EXTRACTORS, tap.namespace)
            assert found_schedule.name == extractor.name

    def test_find_namespace_schedule_custom_extractor(self, subject, create_schedule, custom_tap, project_plugins_service):
        schedule = create_schedule('tap-custom')
        subject.add_schedule(schedule)
        found_schedule = [sched for sched in list(subject.schedules())][0]
        with mock.patch(
            "meltano.core.project_plugins_service.ProjectPluginsService",
            return_value=project_plugins_service
        ):
            extractor = project_plugins_service.find_plugin_by_namespace(PluginType.EXTRACTORS, custom_tap.namespace)
            assert found_schedule.name == extractor.name