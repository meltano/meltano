"""Cloud history utilities.

- Convert lookback expressions to intervals.
- Process table rows.
"""

from __future__ import annotations

import datetime
import re
import typing as t

import tabulate

if t.TYPE_CHECKING:
    from meltano.cloud.api.types import CloudExecution

MINUTES_IN_HOUR = 60
MINUTES_IN_DAY = MINUTES_IN_HOUR * 24
MINUTES_IN_WEEK = MINUTES_IN_DAY * 7
LOOKBACK_PATTERN = re.compile(
    r"^(?:(?P<weeks>\d{1,3}w)?(?P<days>[1-6]d)?(?P<hours>\d{1,2}h)?(?P<minutes>\d{1,2}m)?)$",  # noqa: E501
)
UTC = datetime.timezone.utc


def process_table_row(row: CloudExecution) -> tuple[str, ...]:
    """Process a table row.

    Args:
        row: The row to process.

    Returns:
        The processed row.
    """
    start_time = datetime.datetime.fromisoformat(row["start_time"])

    if row["end_time"]:
        end_time = datetime.datetime.fromisoformat(row["end_time"])
        td = end_time - start_time
        sec = int(td.total_seconds())
        hours, remainder = divmod(sec, 3600)  # noqa: WPS432
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        duration = "N/A"

    status = (
        "Running"
        if row["status"] not in {"STOPPED", "DELETED"}
        else "Success"
        if row["exit_code"] == 0
        else "Failed"
    )

    return (  # noqa: WPS227
        row["execution_id"],
        row["schedule_name"],
        row["deployment_name"],
        start_time.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S"),
        status,
        duration,
    )


def format_history_table(history: list[CloudExecution], table_format: str) -> str:
    """Format the history as a table.

    Args:
        history: The history to format.

    Returns:
        The formatted history.
    """
    return tabulate.tabulate(
        [process_table_row(execution) for execution in history],
        headers=[
            "Execution ID",
            "Schedule Name",
            "Deployment",
            "Executed At (UTC)",
            "Result",
            "Duration",
        ],
        tablefmt=table_format,
    )


def lookback_to_interval(lookback: str) -> datetime.timedelta:
    """Convert a lookback string to an interval string."""
    m = LOOKBACK_PATTERN.match(lookback)
    if m is None:
        raise ValueError(f"Invalid lookback string: {lookback}")

    weeks, days, hours, minutes = m.groups()

    factor: int
    total = 0

    for value, factor in (
        (minutes, 1),
        (hours, MINUTES_IN_HOUR),
        (days, MINUTES_IN_DAY),
        (weeks, MINUTES_IN_WEEK),
    ):
        if value is not None:
            number = int(value[:-1])
            total += number * factor

    return datetime.timedelta(minutes=total)


def interval_to_lookback(interval: datetime.timedelta) -> str:
    """Convert an interval string to a lookback string."""
    total_minutes = interval.total_seconds() / 60
    weeks, remainder = divmod(total_minutes, MINUTES_IN_WEEK)
    days, remainder = divmod(remainder, MINUTES_IN_DAY)
    hours, minutes = divmod(remainder, MINUTES_IN_HOUR)

    lookback = ""
    if weeks > 0:
        lookback = f"{lookback}{int(weeks)}w"
    if days > 0:
        lookback = f"{lookback}{int(days)}d"
    if hours > 0:
        lookback = f"{lookback}{int(hours)}h"
    if minutes > 0:
        lookback = f"{lookback}{int(minutes)}m"

    return lookback
