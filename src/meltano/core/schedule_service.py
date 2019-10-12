import logging
from collections import namedtuple
from typing import Optional
from datetime import datetime, date

from .plugin.settings_service import PluginSettingsService, PluginSettingMissingError
from .project import Project
from .plugin import PluginType, PluginRef
from .db import project_engine
from .utils import nest, iso8601_datetime, coerce_datetime


class ScheduleAlreadyExistsError(Exception):
    """Occurs when a schedule already exists."""

    def __init__(self, schedule):
        self.schedule = schedule


Schedule = namedtuple(
    "Schedule",
    ("name", "extractor", "loader", "transform", "interval", "start_date", "env"),
)


class ScheduleService:
    def __init__(
        self, project: Project, plugin_settings_service: PluginSettingsService = None
    ):
        self.project = project
        self.plugin_settings_service = plugin_settings_service or PluginSettingsService(
            project
        )

    def add(
        self,
        session,
        name,
        extractor: str,
        loader: str,
        transform: str,
        interval: str,
        start_date: Optional[datetime] = None,
        **env,
    ):
        start_date = coerce_datetime(start_date) or self.default_start_date(
            session, extractor
        )
        schedule = Schedule(
            name, extractor, loader, transform, interval, start_date, env=env
        )

        return self.add_schedule(schedule)

    def default_start_date(self, session, extractor: str) -> datetime:
        """
        Returns the `start_date` of the extractor, or now.
        """
        extractor_ref = PluginRef(PluginType.EXTRACTORS, extractor)
        start_date = None
        try:
            start_date, _ = self.plugin_settings_service.get_value(
                session, extractor_ref, "start_date"
            )
        except PluginSettingMissingError:
            logging.debug(f"`start_date` not found in {extractor}.")

        # TODO: this coercion should be handled by the `kind` attribute
        # on the actual setting
        if isinstance(start_date, date):
            return coerce_datetime(start_date)

        if isinstance(start_date, datetime):
            return start_date

        return iso8601_datetime(start_date) or datetime.utcnow()

    def add_schedule(self, schedule: Schedule):
        with self.project.meltano_update() as meltano:
            # guard if it already exists
            if any(map(lambda s: s.name == schedule.name, self.schedules())):
                raise ScheduleAlreadyExistsError(schedule)

            # find the orchestrator plugin config
            schedules = nest(meltano, "schedules", value=[])
            schedules.append(self.schedule_definition(schedule))

        return schedule

    def schedules(self):
        return (
            self.yaml_schedule(schedule_def)
            for schedule_def in self.project.meltano.get("schedules", [])
        )

    @classmethod
    def schedule_definition(cls, schedule: Schedule) -> dict:
        definition = schedule._asdict()
        return dict(definition)

    @classmethod
    def yaml_schedule(cls, schedule_definition: dict) -> Schedule:
        return Schedule(**schedule_definition)
