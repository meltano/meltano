"""Meltano schedule definition."""
from __future__ import annotations

import datetime

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.job import Job as StateJob
from meltano.core.job import JobFinder as StateJobFinder

CRON_INTERVALS = {
    "@once": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}


class Schedule(NameEq, Canonical):  # noqa: WPS230
    """A schedule is an elt command or a job configured to run at a certain interval."""

    def __init__(
        self,
        name: str,
        extractor: str | None = None,
        loader: str | None = None,
        transform: str | None = None,
        interval: str | None = None,
        start_date: datetime.datetime | None = None,
        job: str | None = None,
        env: dict[str, str] | None = None,
    ):
        """Initialize a Schedule.

        Args:
            name: The name of the schedule.
            extractor: The name of the extractor.
            loader: The name of the loader.
            transform: The transform statement (eg: skip, only, run)
            interval: The interval of the schedule.
            start_date: The start date of the schedule.
            job: The name of the job.
            env: The env for this schedule.
        """
        if not env:
            env = {}

        super().__init__()

        # Attributes will be listed in meltano.yml in this order:
        self.name = name

        self.interval = interval
        self.job = job
        self.env = env

        if self.job:
            self.extractor = None
            self.loader = None
            self.transform = None
            self.start_date = None
        else:
            self.extractor = extractor
            self.loader = loader
            self.transform = transform
            self.start_date = start_date

    @property
    def cron_interval(self) -> str:
        """Return the explicit cron interval expression for a cron alias.

        Returns:
            The cron expression.
        """
        return CRON_INTERVALS.get(self.interval, self.interval)

    @property
    def elt_schedule(self) -> bool:
        """Return whether this schedule is an elt schedule.

        Returns:
            True if this schedule is an elt schedule.
        """
        return not self.job

    @property
    def elt_args(self) -> list[str]:
        """Return the list of arguments to pass to the elt command, if the schedule is an elt schedule.

        Returns:
            The list of arguments to pass to the elt command.

        Raises:
            NotImplementedError: If the schedule is a job.
        """
        if self.job:
            raise NotImplementedError
        return [
            self.extractor,
            self.loader,
            f"--transform={self.transform}",
            f"--state-id={self.name}",
        ]

    def last_successful_run(self, session) -> StateJob:
        """Return the last successful run for this schedule.

        Args:
            session: The database session.

        Returns:
            The last successful run for this schedule.

        Raises:
            NotImplementedError: If the schedule is a job.
        """
        if self.job:
            raise NotImplementedError(
                "Can't obtain last successful State(Job) for schedule job."
            )
        return StateJobFinder(self.name).latest_success(session)
