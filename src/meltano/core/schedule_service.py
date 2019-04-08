from collections import namedtuple

from .config_service import ConfigService
from .project import Project
from .utils import nest


class ScheduleAlreadyExistsError(Exception):
    """Occurs when a schedule already exists."""

    pass


Schedule = namedtuple(
    "Schedule", ("name", "extractor", "loader", "transform", "interval", "env")
)


class ScheduleService:
    def __init__(self, project: Project):
        self.project = project

    def add(
        self, name, extractor: str, loader: str, transform: str, interval: str, **env
    ):
        schedule = Schedule(name, extractor, loader, transform, interval, env=env)

        return self.add_schedule(schedule)

    def add_schedule(self, schedule: Schedule):
        # guard if it already exists
        if any(map(lambda s: s.name == schedule.name, self.schedules())):
            raise ScheduleAlreadyExistsError()

        with self.project.meltano_update() as meltano:
            # find the orchestrator plugin config
            schedules = nest(meltano, "schedules", value=[])
            schedules.append(dict(schedule._asdict()))

        return schedule

    def schedules(self):
        return (
            Schedule(**schedule_def)
            for schedule_def in self.project.meltano.get("schedules", [])
        )
