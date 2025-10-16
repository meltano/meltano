"""Service for managing meltano schedules."""

from __future__ import annotations

import typing as t

import structlog

from meltano.core.error import MeltanoError
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.plugin import PluginType
from meltano.core.plugin.error import PluginNotFoundError
from meltano.core.schedule import (
    CRON_INTERVALS,
    ELTSchedule,
    JobSchedule,
    Schedule,
    is_valid_cron,
)
from meltano.core.task_sets_service import TaskSetsService
from meltano.core.utils import NotFound, find_named

if t.TYPE_CHECKING:
    import subprocess

    from meltano.core.project import Project

logger = structlog.stdlib.get_logger(__name__)


class ScheduleAlreadyExistsError(MeltanoError):
    """A schedule already exists."""

    def __init__(self, schedule: Schedule):
        """Initialize the exception.

        Args:
            schedule: The schedule that already exists.
        """
        self.schedule = schedule
        super().__init__(reason=f"Schedule '{self.schedule.name}' already exists")


class ScheduleDoesNotExistError(MeltanoError):
    """A schedule does not exist."""

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
    """A schedule for a namespace cannot be found."""

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
    """A cron expression is invalid."""

    def __init__(self, cron: str):
        """Initialize the exception.

        Args:
            cron: The cron expression that is invalid.
        """
        self.cron = cron

        reason = f"Invalid Cron expression or alias: '{self.cron}'"
        instruction = "Please use a valid cron expression"
        super().__init__(reason, instruction)


_S = t.TypeVar("_S", bound=Schedule)


class ScheduleService:
    """Service for managing schedules."""

    def __init__(self, project: Project):
        """Initialize a ScheduleService for a project to manage a projects schedules.

        Args:
            project: The project whose schedules you wish to interact with.
        """
        self.project = project
        self.task_sets_service = TaskSetsService(project)

    def add_elt(
        self,
        name: str,
        extractor: str,
        loader: str,
        transform: str,
        interval: str,
        **env: str,
    ) -> ELTSchedule:
        """Add a scheduled legacy elt task.

        Args:
            session: The active sqlalchemy session.
            name: The name of the schedule.
            extractor:  The name of the extractor.
            loader: The name of the loader.
            transform: The transform statement (eg: skip, only, run)
            interval: The interval of the elt job.
            env: The env for this scheduled elt job.

        Returns:
            The added schedule.
        """
        schedule = ELTSchedule(
            name=name,
            extractor=extractor,
            loader=loader,
            transform=transform,
            interval=interval,
            env=env,
        )
        return self.add_schedule(schedule)

    def add(self, name: str, job: str, interval: str, **env: str) -> JobSchedule:
        """Add a scheduled job.

        Args:
            name: The name of the schedule.
            job: The name of the job.
            interval: The interval of the job.
            env: The env for this scheduled job

        Returns:
            The added schedule.
        """
        return self.add_schedule(
            JobSchedule(
                name=name,
                job=job,
                interval=interval,
                env=env,
            ),
        )

    def add_schedule(self, schedule: _S) -> _S:
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
            and schedule.interval not in CRON_INTERVALS
            and not is_valid_cron(schedule.interval)
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
            except NotFound as ex:
                raise ScheduleDoesNotExistError(name) from ex

            # find the schedules plugin config
            meltano.schedules.remove(schedule)

        return name

    def update_schedule(self, schedule: Schedule) -> None:
        """Update a schedule.

        Args:
            schedule: The schedule to update.

        Raises:
            ScheduleDoesNotExistError: If the schedule doesn't exist.
        """
        with self.project.meltano_update() as meltano:
            try:
                idx = meltano.schedules.index(schedule)
            except ValueError:
                raise ScheduleDoesNotExistError(schedule.name) from None
            else:
                meltano.schedules[idx] = schedule

    def find_namespace_schedule(self, namespace: str) -> Schedule:
        """Search for a Schedule that runs for a certain plugin namespace.

        Example:
            `tap_carbon` would yield the first schedule that runs for the
            `tap-carbon` extractor.

        Args:
            namespace: The plugin namespace to search.

        Returns:
            The schedule

        Raises:
            ScheduleNotFoundError: If no schedule is found.
        """
        try:
            extractor = self.project.plugins.find_plugin_by_namespace(
                PluginType.EXTRACTORS,
                namespace,
            )

            return next(
                schedule
                for schedule in self.schedules()
                if isinstance(schedule, ELTSchedule)
                and schedule.extractor == extractor.name
            )
        except (PluginNotFoundError, StopIteration) as err:
            raise ScheduleNotFoundError(namespace) from err

    def schedules(self) -> list[Schedule]:
        """Return all schedules in the project.

        Returns:
            The list of schedules.
        """
        return self.project.meltano.schedules.copy()

    def find_schedule(self, name: str) -> Schedule:
        """Find a schedule by name.

        Args:
            name: the name of the schedule to find

        Returns:
            Schedule: the schedule with the given name

        Raises:
            ScheduleNotFoundError: if the schedule does not exist
        """
        return find_named(self.schedules(), name)

    def run(
        self,
        schedule: Schedule,
        *args: str,
        env: dict | None = None,
        **kwargs: t.Any,
    ) -> subprocess.CompletedProcess[str]:
        """Run a scheduled elt task or named job.

        Args:
            schedule: The schedule whos elt task or named job to run.
            args: The arguments to pass to the elt task or named job.
            env: The environment to run the elt task or named job in.
            kwargs: The keyword arguments to pass to the elt task or named job.

        Returns:
            The completed process.
        """
        env = env or {}
        if isinstance(schedule, JobSchedule):
            return MeltanoInvoker(self.project).invoke(
                ["run", *args, schedule.job],
                env={**schedule.env, **env},
                **kwargs,
            )

        if isinstance(schedule, ELTSchedule):
            return MeltanoInvoker(self.project).invoke(
                ["elt", *schedule.elt_args, *args],
                env={**schedule.env, **env},
                **kwargs,
            )

        # no cover: start
        msg = f"Invalid schedule type: {type(schedule)}"
        raise ValueError(msg)
        # no cover: stop
