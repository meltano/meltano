import pytest

from meltano.core.schedule_service import (
    ScheduleService,
    Schedule,
    ScheduleAlreadyExistsError,
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
