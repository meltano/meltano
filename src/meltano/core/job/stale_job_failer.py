"""Defines `fail_stale_jobs`."""

from __future__ import annotations

import typing as t

import structlog

from .finder import JobFinder

if t.TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = structlog.stdlib.get_logger(__name__)


def fail_stale_jobs(session: Session, state_id: str | None = None) -> None:
    """Mark stale jobs as failed.

    Args:
        session: An ORM DB session.
        state_id: If provided, only jobs with this state ID will be failed if stale.
    """
    finder = JobFinder.all_stale if state_id is None else JobFinder(state_id).stale
    for job in finder(session):
        if not job.fail_stale():
            continue

        job.save(session)

        # No need to mention state ID if they're all going to be the same.
        with_state_id = "" if state_id else f" with state ID '{job.job_name}'"

        error = job.payload["error"]
        logger.info(
            f"Marked stale run{with_state_id} that started at "  # noqa: G004
            f"{job.started_at} as failed: {error}",
        )
