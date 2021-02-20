import logging
from collections import namedtuple
from datetime import date, datetime
from typing import Optional

from .db import project_engine
from .meltano_invoker import MeltanoInvoker
from .plugin import PluginRef, PluginType
from .plugin.settings_service import PluginSettingsService, SettingMissingError
from .plugin_discovery_service import PluginDiscoveryService, PluginNotFoundError
from .project import Project
from .project_plugins_service import ProjectPluginsService
from .schedule import Schedule
from .utils import NotFound, coerce_datetime, find_named, iso8601_datetime, nest


class ScheduleAlreadyExistsError(Exception):
    """Occurs when a schedule already exists."""

    def __init__(self, schedule):
        self.schedule = schedule


class ScheduleDoesNotExistError(Exception):
    """Occurs when a schedule does not exist."""

    def __init__(self, name):
        self.name = name


class ScheduleNotFoundError(Exception):
    """Occurs when a schedule for a namespace cannot be found."""

    def __init__(self, namespace):
        self.namespace = namespace


class ScheduleService:
    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

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
        start_date = coerce_datetime(start_date) or self.default_start_date(  # TODO
            session, extractor
        )

        schedule = Schedule(
            name, extractor, loader, transform, interval, start_date, env=env
        )

        return self.add_schedule(schedule)

    def remove(self, name):
        return self.remove_schedule(name)

    def default_start_date(self, session, extractor: str) -> datetime:
        """
        Returns the `start_date` of the extractor, or now.
        """
        extractor = self.plugins_service.find_plugin(
            extractor, plugin_type=PluginType.EXTRACTORS
        )
        start_date = None
        try:
            settings_service = PluginSettingsService(
                self.project, extractor, plugins_service=self.plugins_service
            )
            start_date = settings_service.get("start_date", session=session)
        except SettingMissingError:
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
            if schedule in meltano.schedules:
                raise ScheduleAlreadyExistsError(schedule)

            meltano.schedules.append(schedule)

        return schedule

    def remove_schedule(self, name: str):
        with self.project.meltano_update() as meltano:
            try:
                # guard if it doesn't exist
                schedule = find_named(self.schedules(), name)
            except NotFound:
                raise ScheduleDoesNotExistError(name)

            # find the schedules plugin config
            meltano.schedules.remove(schedule)

        return name

    def update_schedule(self, schedule: Schedule):
        with self.project.meltano_update() as meltano:
            try:
                idx = meltano.schedules.index(schedule)
                meltano.schedules[idx] = schedule
            except ValueError:
                raise ScheduleDoesNotExistError(schedule.name)

    def find_namespace_schedule(self, namespace: str) -> Schedule:

        """
        Search for a Schedule that runs for a certain plugin namespace.
        For instance, `tap_carbon` would yield the first schedule that
        runs for the `tap-carbon` extractor.
        """

        try:
            extractor = self.plugins_service.find_plugin_by_namespace(
                PluginType.EXTRACTORS, namespace
            )

            return next(
                schedule
                for schedule in self.schedules()
                if schedule.extractor == extractor.name
            )
        except (PluginNotFoundError, StopIteration) as err:
            raise ScheduleNotFoundError(namespace) from err

    def schedules(self):
        return self.project.meltano.schedules

    def find_schedule(self, name):
        try:
            return find_named(self.schedules(), name)
        except StopIteration as err:
            raise ScheduleNotFoundError(name) from err

    def run(self, schedule, *args, env={}, **kwargs):
        return MeltanoInvoker(self.project).invoke(
            ["elt", *schedule.elt_args, *args], env={**schedule.env, **env}, **kwargs
        )
