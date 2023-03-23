"""Static types for the Meltano Cloud client."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class CloudExecution(TypedDict):
    """Cloud execution details."""

    execution_id: str
    start_time: str
    end_time: str | None
    status: str
    exit_code: int

    environment_name: str
    schedule_name: str
    job_name: str
