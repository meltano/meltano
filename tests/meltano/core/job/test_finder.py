from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from meltano.core.job.finder import JobFinder
from meltano.core.job.job import (
    HEARTBEAT_VALID_MINUTES,
    HEARTBEATLESS_JOB_VALID_HOURS,
    Job,
    State,
)


class TestJobFinder:
    @pytest.mark.parametrize(
        ("state", "started_at_hours_ago", "last_heartbeat_at_minutes_ago", "is_stale"),
        (
            (State.RUNNING, None, None, False),
            (State.RUNNING, HEARTBEATLESS_JOB_VALID_HOURS - 1, None, False),
            (State.RUNNING, HEARTBEATLESS_JOB_VALID_HOURS + 1, None, True),
            (State.RUNNING, None, 0, False),
            (State.RUNNING, None, HEARTBEAT_VALID_MINUTES - 1, False),
            (State.RUNNING, None, HEARTBEAT_VALID_MINUTES + 1, True),
            (State.SUCCESS, None, None, False),
            (State.FAIL, None, None, False),
        ),
    )
    def test_all_stale(
        self,
        state,
        started_at_hours_ago,
        last_heartbeat_at_minutes_ago,
        is_stale,
        session,
    ) -> None:
        started_at = datetime.now(timezone.utc)
        if started_at_hours_ago:
            started_at -= timedelta(hours=started_at_hours_ago)

        last_heartbeat_at = None
        if last_heartbeat_at_minutes_ago is not None:
            last_heartbeat_at = datetime.now(timezone.utc) - timedelta(
                minutes=last_heartbeat_at_minutes_ago,
            )

        job = Job(
            job_name="test_state_id",
            state=state,
            started_at=started_at,
            last_heartbeat_at=last_heartbeat_at,
        )
        job.save(session)

        assert job.is_stale() == is_stale

        assert bool(job in JobFinder.all_stale(session)) == is_stale

    def test_stale(self, session) -> None:
        job = Job(job_name="test")
        job.start()
        job.last_heartbeat_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        job.save(session)

        assert job in JobFinder(state_id=job.job_name).stale(session)

        assert job not in JobFinder(state_id="other").stale(session)
