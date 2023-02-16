"""Schemas for the Meltano Cloud API."""

from __future__ import annotations

from pydantic import BaseModel


class RunRequestData(BaseModel):
    """Request to run a job or schedule."""

    job_or_schedule_id: str
