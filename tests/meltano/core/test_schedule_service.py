import pytest
from datetime import datetime
from freezegun import freeze_time
from unittest import mock

from meltano.core.schedule_service import (
    ScheduleService,
    Schedule,
    ScheduleAlreadyExistsError,
    PluginSettingMissingError,
)


@pytest.fixture
def subject(session, schedule_service_factory):
    return schedule_service_factory(session)


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


@freeze_time("2000-01-01")
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

    def test_schedule_start_date(self, subject, tap, target):
        # curry the `add` method to remove some arguments
        add = lambda name, start_date: subject.add(
            name, tap.name, target.name, "run", "@daily", start_date=start_date
        )

        # when a start_date is set, the schedule should use it
        schedule = add("with_start_date", datetime(2001, 1, 1))
        assert schedule.start_date == datetime(2001, 1, 1)

        # or use datetime.utcnow()
        schedule = subject.add(
            "without_start_date",
            tap.name,
            target.name,
            "run",
            "@daily",
            start_date=None,
        )

        assert schedule.start_date == datetime.utcnow()

        # or use the start_date in the extractor configuration
        subject.plugin_settings_service.set(tap, "start_date", datetime(2002, 1, 1))
        schedule = add("with_default_start_date", None)
        assert schedule.start_date == datetime(2002, 1, 1)

        # or default to `utcnow()` if the plugin exposes no config
        with mock.patch(
            "meltano.core.schedule_service.PluginSettingsService.get_value",
            side_effect=PluginSettingMissingError(tap, "start_date"),
        ):
            schedule = add("with_no_start_date", None)
            assert schedule.start_date == datetime.utcnow()
