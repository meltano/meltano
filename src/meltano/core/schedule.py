import datetime

from meltano.core.behavior.canonical import Canonical
from meltano.core.behavior import NameEq
from meltano.core.job import JobFinder

CRON_INTERVALS = {
    "@once": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}


class Schedule(NameEq, Canonical):
    def __init__(
        self,
        name: str = None,
        extractor: str = None,
        loader: str = None,
        transform: str = None,
        interval: str = None,
        start_date: datetime = None,
        env={},
    ):
        super().__init__()

        # Attributes will be listed in meltano.yml in this order:
        self.name = name
        self.extractor = extractor
        self.loader = loader
        self.transform = transform
        self.interval = interval
        self.start_date = start_date
        self.env = env

    @property
    def cron_interval(self):
        return CRON_INTERVALS.get(self.interval, self.interval)

    @property
    def elt_args(self):
        return [
            self.extractor,
            self.loader,
            f"--transform={self.transform}",
            f"--job_id={self.name}",
        ]

    def last_successful_run(self, session):
        return JobFinder(self.name).latest_success(session)
