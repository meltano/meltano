"""Meltano schedule definition."""

from __future__ import annotations

import typing as t

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical
from meltano.core.job import JobFinder as StateJobFinder

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from meltano.core.job import Job as StateJob

CRON_INTERVALS: dict[str, str | None] = {
    "@once": None,
    "@manual": None,
    "@none": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@midnight": "0 0 * * *",
}

# Field ranges: min, max
FIELD_RANGES = (
    (0, 59),  # minute
    (0, 23),  # hour
    (1, 31),  # day
    (1, 12),  # month
    (0, 6),  # dow
)

# Month and day of week aliases
MONTH_ALIASES = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

DOW_ALIASES = {
    "sun": 0,
    "mon": 1,
    "tue": 2,
    "wed": 3,
    "thu": 4,
    "fri": 5,
    "sat": 6,
}

# Predefined aliases
CRON_ALIASES = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def is_valid_cron(expression: str) -> bool:
    """Check if a cron expression is valid.

    Args:
        expression: The cron expression to validate

    Returns:
        True if the expression is valid, False otherwise
    """
    # Handle predefined aliases
    expr = expression.strip().lower()
    if _expr := CRON_INTERVALS.get(expr):
        expr = _expr

    # Split into fields
    fields = expr.split()

    # Valid cron expressions have 5
    # TODO: Consider supporting seconds and year fields
    if len(fields) != 5:
        return False

    # Validate each field
    return all(_is_valid_field(field, i) for i, field in enumerate(fields))


def _is_valid_field(field: str, field_index: int, /) -> bool:
    """Validate a single cron field."""
    # Handle wildcards
    if field == "*":
        return True

    # Handle question mark (only valid for day and dow fields)
    if field == "?":
        return field_index in {2, 4}  # day or dow

    # Handle "L" (last day of month, only valid for day field)
    if field == "l":
        return field_index == 2  # day field

    # Split by commas for multiple values
    min_val, max_val = FIELD_RANGES[field_index]
    return any(
        _is_valid_field_part(part, field_index, min_val, max_val)
        for part in field.split(",")
    )


def _is_valid_field_part(
    part: str,
    field_index: int,
    min_val: int,
    max_val: int,
    /,
) -> bool:
    """Validate a single part of a cron field."""
    # Handle step values (e.g., "*/2", "1-5/2")
    if "/" in part:
        base, step = part.split("/", 1)
        if not step.isdigit() or int(step) <= 0:
            return False

        # If base is empty after split, it means it was like "/2"
        if not base:
            return False

        # Handle "*" as base (e.g., "*/5")
        if base == "*":
            return True

        # Validate the base part
        return _is_valid_field_part(base, field_index, min_val, max_val)

    # Handle ranges (e.g., "1-5")
    if "-" in part:
        start, end = part.split("-", 1)
        start_val = _parse_value(start, field_index)
        end_val = _parse_value(end, field_index)

        if start_val is None or end_val is None:
            return False

        # Allow wrap-around ranges like "fri-mon"
        if start_val > end_val and field_index == 4:  # dow field
            return True

        # Handle day of week special case: 7 = Sunday (0)
        if end_val == 7 and field_index == 4:
            end_val = 0

        return min_val <= start_val <= max_val and min_val <= end_val <= max_val

    # Handle single values
    value = _parse_value(part, field_index)
    if value is None:
        return False

    # Special handling for day of week field to allow 7 as Sunday
    if field_index == 4 and value == 7:
        return True

    return min_val <= value <= max_val


def _parse_value(value: str, field_index: int, /) -> int | None:
    """Parse a value, handling aliases and special cases."""
    if not value:
        return None

    # Handle numeric values
    if value.isdigit():
        return int(value)

    # Handle month aliases
    if field_index == 3 and value in MONTH_ALIASES:
        return MONTH_ALIASES[value]

    # Handle day of week aliases
    if field_index == 4 and value in DOW_ALIASES:
        return DOW_ALIASES[value]

    # Handle "L" for last day
    if value == "l":
        return 31 if field_index == 2 else None

    return None


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
        **kwargs: t.Any,
    ):
        """Initialize a Schedule.

        Args:
            name: The name of the schedule.
            interval: The interval of the schedule.
            env: The env for this schedule.
            kwargs: The keyword arguments to initialize the schedule with.
        """
        super().__init__(**kwargs)

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
        return (
            CRON_INTERVALS.get(self.interval, self.interval) if self.interval else None
        )


class ELTSchedule(Schedule):
    """A schedule is an elt command or a job configured to run at a certain interval."""

    extractor: str
    loader: str
    transform: str

    def __init__(
        self,
        *,
        extractor: str,
        loader: str,
        transform: str,
        **kwargs: t.Any,
    ):
        """Initialize a Schedule.

        Args:
            extractor: The name of the extractor.
            loader: The name of the loader.
            transform: The transform statement (eg: skip, only, run)
            kwargs: The keyword arguments to initialize the schedule with.
        """
        super().__init__(**kwargs)
        self.extractor = extractor
        self.loader = loader
        self.transform = transform

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
