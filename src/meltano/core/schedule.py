"""Meltano schedule definition."""

from __future__ import annotations

import typing as t

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.job import Job as StateJob
from meltano.core.job import JobFinder as StateJobFinder

if t.TYPE_CHECKING:
    import datetime

    from sqlalchemy.orm import Session

CRON_INTERVALS: dict[str, str | None] = {
    "@once": None,
    "@manual": None,
    "@none": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}


class Schedule(NameEq, Canonical):
    """A base schedule class."""

    name: str
    interval: str | None
    env: dict[str, str]

    def __init__(
        self,
        *,
        name: str,
        interval: str | None,
        env: dict[str, str] | None = None,
    ):
        """Initialize a Schedule.

        Args:
            name: The name of the schedule.
            interval: The interval of the schedule.
            env: The env for this schedule.
        """
        super().__init__()

        # Attributes will be listed in meltano.yml in this order:
        self.name = name
        self.interval = interval
        self.env = env or {}

    @property
    def cron_interval(self) -> str | None:
        """Return the explicit cron interval expression for a cron alias.

        Returns:
            The cron expression.
        """
        if self.interval:
            return CRON_INTERVALS.get(self.interval, self.interval)
        return None


class ELTSchedule(Schedule):
    """A schedule is an elt command or a job configured to run at a certain interval."""

    extractor: str
    loader: str
    transform: str
    start_date: datetime.datetime | None

    def __init__(
        self,
        *,
        extractor: str,
        loader: str,
        transform: str,
        start_date: datetime.datetime | None = None,
        **kwargs: t.Any,
    ):
        """Initialize a Schedule.

        Args:
            extractor: The name of the extractor.
            loader: The name of the loader.
            transform: The transform statement (eg: skip, only, run)
            start_date: The start date of the schedule.
            kwargs: The keyword arguments to initialize the schedule with.
        """
        super().__init__(**kwargs)
        self.extractor = extractor
        self.loader = loader
        self.transform = transform
        self.start_date = start_date

    @property
    def elt_args(self) -> list[str]:
        """Return the list of arguments to pass to the elt command.

        Only valid if the schedule is an elt schedule.

        Returns:
            The list of arguments to pass to the elt command.

        Raises:
            NotImplementedError: If the schedule is a job.
        """
        return [
            t.cast("str", self.extractor),
            t.cast("str", self.loader),
            f"--transform={self.transform}",
            f"--state-id={self.name}",
        ]

    def last_successful_run(self, session: Session) -> StateJob | None:
        """Return the last successful run for this schedule.

        Args:
            session: The database session.

        Returns:
            The last successful run for this schedule.

        Raises:
            NotImplementedError: If the schedule is a job.
        """
        return StateJobFinder(self.name).latest_success(session)


class JobSchedule(Schedule):
    """A schedule is a job configured to run at a certain interval."""

    job: str

    def __init__(self, *, job: str, **kwargs: t.Any) -> None:
        """Initialize a Schedule.

        Args:
            job: The name of the job.
            kwargs: The keyword arguments to initialize the schedule with.
        """
        super().__init__(**kwargs)
        self.job = job
