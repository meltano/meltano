import pytest
from datetime import datetime
from unittest import mock

from meltano.core.schedule_service import (
    ScheduleService,
    Schedule,
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    PluginSettingMissingError,
)


@pytest.fixture
def subject(schedule_service):
    return schedule_service


@pytest.fixture
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


class TestScheduleService:
    def test_add_schedule(self, subject, create_schedule):
        COUNT = 10

        schedules = [create_schedule(f"schedule_{i}") for i in range(COUNT)]
        for schedule in schedules:
            subject.add_schedule(schedule)

        assert list(subject.schedules()) == schedules

        # but name must be unique
        with pytest.raises(ScheduleAlreadyExistsError):
            subject.add_schedule(schedules[0])

    def test_remove_schedule(self, subject):
        schedules_list = list(subject.schedules())
        assert len(schedules_list) == 10

        idx = 3
        target_schedule = schedules_list[idx]
        target_name = f"schedule_{idx}"
        assert target_schedule.name == target_name

        subject.remove_schedule(target_name)
        schedules_list = list(subject.schedules())
        assert len(schedules_list) == 9
        assert target_schedule not in schedules_list

        # schedule name must exist to be removed
        with pytest.raises(ScheduleDoesNotExistError):
            subject.remove_schedule(target_name)

    def test_schedule_start_date(self, subject, session, tap, target):
        # curry the `add` method to remove some arguments
        add = lambda name, start_date: subject.add(
            session, name, tap.name, target.name, "run", "@daily", start_date=start_date
        )

        # when a start_date is set, the schedule should use it
        schedule = add("with_start_date", datetime(2001, 1, 1))
        assert schedule.start_date == datetime(2001, 1, 1)

        # or use the start_date in the extractor configuration
        subject.plugin_settings_service.set(
            session, tap, "start_date", datetime(2002, 1, 1)
        )
        schedule = add("with_default_start_date", None)
        assert schedule.start_date == datetime(2002, 1, 1)

        # or default to `utcnow()` if the plugin exposes no config
        with mock.patch(
            "meltano.core.schedule_service.PluginSettingsService.get_value",
            side_effect=PluginSettingMissingError(tap, "start_date"),
        ):
            schedule = add("with_no_start_date", None)
            assert schedule.start_date
