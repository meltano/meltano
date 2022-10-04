"""Service for managing meltano schedules."""

from __future__ import annotations

import logging
import subprocess
from datetime import date, datetime

from croniter import croniter

from meltano.core.error import MeltanoError
from meltano.core.setting_definition import SettingMissingError

from .meltano_invoker import MeltanoInvoker
from .plugin import PluginType
from .plugin.settings_service import PluginSettingsService
from .plugin_discovery_service import PluginNotFoundError
from .project import Project
from .project_plugins_service import ProjectPluginsService
from .schedule import Schedule
from .task_sets_service import TaskSetsService
from .utils import NotFound, coerce_datetime, find_named, iso8601_datetime


class ScheduleAlreadyExistsError(MeltanoError):
    """Occurs when a schedule already exists."""

    def __init__(self, schedule: Schedule):
        """Initialize the exception.

        Args:
            schedule: The schedule that already exists.
        """
        self.schedule = schedule
        super().__init__(reason=f"Schedule '{self.schedule.name}' already exists")


class ScheduleDoesNotExistError(MeltanoError):
    """Occurs when a schedule does not exist."""

    def __init__(self, name: str):
        """Initialize the exception.

        Args:
            name: The name of the schedule that does not exist.

        """
        self.name = name

        super().__init__(
            reason=f"Schedule '{name}' does not exist",
            instruction="Use `meltano schedule add` to add a schedule",
        )


class ScheduleNotFoundError(MeltanoError):
    """Occurs when a schedule for a namespace cannot be found."""

    def __init__(self, namespace: str):
        """Initialize the exception.

        Args:
            namespace: The namespace that had no associated schedules.
        """
        self.namespace = namespace

        reason = f"No schedule found for namespace {self.namespace}"
        instruction = "Use `meltano schedule add` to add a schedule"
        super().__init__(reason, instruction)


class BadCronError(MeltanoError):
    """Occurs when a cron expression is invalid."""

    def __init__(self, cron: str):
        """Initialize the exception.

        Args:
            cron: The cron expression that is invalid.
        """
        self.cron = cron

        reason = f"Invalid Cron expression or alias: '{self.cron}'"
        instruction = "Please use a valid cron expression"
        super().__init__(reason, instruction)


class ScheduleService:
    """Service for managing schedules."""

    def __init__(self, project: Project, plugins_service: ProjectPluginsService = None):
        """Initialize a ScheduleService for a project to manage a projects schedules.

        Args:
            project: The project whos schedules you wish to interact with.
            plugins_service: The project plugins service.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)
        self.task_sets_service = TaskSetsService(project)

    def add_elt(
        self,
        session,
        name,
        extractor: str,
        loader: str,
        transform: str,
        interval: str,
        start_date: datetime | None = None,
        **env,
    ) -> Schedule:
        """Add a scheduled legacy elt task.

        Args:
            session: The active sqlalchemy session.
            name: The name of the schedule.
            extractor:  The name of the extractor.
            loader: The name of the loader.
            transform: The transform statement (eg: skip, only, run)
            interval: The interval of the elt job.
            start_date: The start date of the elt job.
            env: The env for this scheduled elt job.

        Returns:
            The added schedule.
        """
        start_date = coerce_datetime(start_date) or self.default_start_date(  # TODO
            session, extractor
        )

        schedule = Schedule(
            name, extractor, loader, transform, interval, start_date, env=env
        )
        return self.add_schedule(schedule)

    def add(self, name: str, job: str, interval: str, **env) -> Schedule:
        """Add a scheduled job.

        Args:
            name: The name of the schedule.
            job: The name of the job.
            interval: The interval of the job.
            env: The env for this scheduled job

        Returns:
            The added schedule.
        """
        schedule = Schedule(name=name, job=job, interval=interval, env=env)
        self.add_schedule(schedule)
        return schedule

    def remove(self, name) -> str:
        """Remove a schedule from the project.

        Args:
            name: The name of the schedule.

        Returns:
            The name of the removed schedule.
        """
        return self.remove_schedule(name)

    def default_start_date(self, session, extractor: str) -> datetime:
        """Obtain the default start date for an elt schedule.

        Args:
            session: The session to use.
            extractor: The extractor to get the start_date from.

        Returns:
            The start_date of the extractor, or now.
        """
        extractor_plugin = self.plugins_service.find_plugin(
            extractor, plugin_type=PluginType.EXTRACTORS
        )
        start_date: str | datetime | date | None = None
        try:
            settings_service = PluginSettingsService(
                self.project, extractor_plugin, plugins_service=self.plugins_service
            )
            start_date = settings_service.get("start_date", session=session)
        except SettingMissingError:
            logging.debug(f"`start_date` not found in {extractor_plugin}.")

        # TODO: this coercion should be handled by the `kind` attribute
        # on the actual setting
        if isinstance(start_date, date):
            return coerce_datetime(start_date)

        if isinstance(start_date, datetime):
            return start_date

        return iso8601_datetime(start_date) or datetime.utcnow()

    def add_schedule(self, schedule: Schedule) -> Schedule:
        """Add a schedule to the project.

        Args:
            schedule: The schedule to add.

        Returns:
            The added schedule.

        Raises:
            BadCronError: If the cron expression is invalid.
            ScheduleAlreadyExistsError: If a schedule with the same name already exists.
        """
        if (
            schedule.interval is not None
            and schedule.interval != "@once"
            and not croniter.is_valid(schedule.interval)
        ):
            raise BadCronError(schedule.interval)

        with self.project.meltano_update() as meltano:
            # guard if it already exists
            if schedule in meltano.schedules:
                raise ScheduleAlreadyExistsError(schedule)

            meltano.schedules.append(schedule)

        return schedule

    def remove_schedule(self, name: str) -> str:
        """Remove a schedule.

        Args:
            name: The name of the schedule.

        Returns:
            The name of the schedule.

        Raises:
            ScheduleDoesNotExistError: If the schedule does not exist.
        """
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
        """Update a schedule.

        Args:
            schedule: The schedule to update.

        Raises:
            ScheduleDoesNotExistError: If the schedule doesn't exist.
        """
        with self.project.meltano_update() as meltano:
            try:
                idx = meltano.schedules.index(schedule)
                meltano.schedules[idx] = schedule
            except ValueError:
                raise ScheduleDoesNotExistError(schedule.name)

    def find_namespace_schedule(self, namespace: str) -> Schedule:
        """Search for a Schedule that runs for a certain plugin namespace.

        Example:
            `tap_carbon` would yield the first schedule that runs for the `tap-carbon` extractor.

        Args:
            namespace: The plugin namespace to search.

        Returns:
            The schedule

        Raises:
            ScheduleNotFoundError: If no schedule is found.
        """
        try:
            extractor = self.plugins_service.find_plugin_by_namespace(
                PluginType.EXTRACTORS, namespace
            )

            return next(
                schedule
                for schedule in self.schedules()
                if not schedule.job and schedule.extractor == extractor.name
            )
        except (PluginNotFoundError, StopIteration) as err:
            raise ScheduleNotFoundError(namespace) from err

    def schedules(self) -> list[Schedule]:
        """Return all schedules in the project.

        Returns:
            The list of schedules.
        """
        return self.project.meltano.schedules.copy()

    def find_schedule(self, name) -> Schedule:
        """Find a schedule by name.

        Args:
            name: the name of the schedule to find

        Returns:
            Schedule: the schedule with the given name

        Raises:
            ScheduleNotFoundError: if the schedule does not exist
        """
        try:
            return find_named(self.schedules(), name)
        except StopIteration as err:
            raise ScheduleNotFoundError(name) from err

    def run(
        self, schedule: Schedule, *args, env: dict = None, **kwargs
    ) -> subprocess.CompletedProcess:
        """Run a scheduled elt task or named job.

        Args:
            schedule: The schedule whos elt task or named job to run.
            args: The arguments to pass to the elt task or named job.
            env: The environment to run the elt task or named job in.
            kwargs: The keyword arguments to pass to the elt task or named job.

        Returns:
            The completed process.
        """
        if env is None:
            env = {}

        if schedule.job:
            return MeltanoInvoker(self.project).invoke(
                ["run", *args, schedule.job],
                env={**schedule.env, **env},
                **kwargs,
            )

        return MeltanoInvoker(self.project).invoke(
            ["elt", *schedule.elt_args, *args], env={**schedule.env, **env}, **kwargs
        )
