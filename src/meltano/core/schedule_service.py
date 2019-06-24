from collections import namedtuple
from typing import Optional
from datetime import datetime

from .config_service import ConfigService
from .plugin.settings_service import PluginSettingsService
from .project import Project
from .plugin import PluginType
from .db import project_engine
from .utils import nest, iso8601_datetime


class ScheduleAlreadyExistsError(Exception):
    """Occurs when a schedule already exists."""

    def __init__(self, schedule):
        self.schedule = schedule


Schedule = namedtuple(
    "Schedule",
    ("name", "extractor", "loader", "transform", "interval", "start_date", "env"),
)


class ScheduleService:
    def __init__(self, project: Project):
        self.project = project

    def add(
        self,
        name,
        extractor: str,
        loader: str,
        transform: str,
        interval: str,
        start_date: Optional[datetime] = None,
        **env
    ):
        # default to the extractor start date
        if not start_date:
            config_service = ConfigService(self.project)
            extractor_plugin = config_service.get_plugin(
                extractor, plugin_type=PluginType.EXTRACTORS
            )

            _, Session = project_engine(self.project)
            session = Session()
            try:
                extractor_settings = PluginSettingsService(
                    session, self.project, extractor_plugin
                )
                start_date = iso8601_datetime(
                    extractor_settings.get_value("start_date")
                )
            finally:
                session.close()

        schedule = Schedule(
            name, extractor, loader, transform, interval, start_date, env=env
        )

        return self.add_schedule(schedule)

    def add_schedule(self, schedule: Schedule):
        # guard if it already exists
        if any(map(lambda s: s.name == schedule.name, self.schedules())):
            raise ScheduleAlreadyExistsError(schedule)

        with self.project.meltano_update() as meltano:
            # find the orchestrator plugin config
            schedules = nest(meltano, "schedules", value=[])
            schedules.append(dict(schedule._asdict()))

        return schedule

    def schedules(self):
        return (
            self.yaml_schedule(schedule_def)
            for schedule_def in self.project.meltano.get("schedules", [])
        )

    @classmethod
    def yaml_schedule(cls, schedule_definition: dict) -> Schedule:
        return Schedule(**schedule_definition)
