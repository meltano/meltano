from __future__ import annotations

import asyncio
import platform
import signal
import typing as t
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from meltano.core.job.job import (
    HEARTBEAT_VALID_MINUTES,
    HEARTBEATLESS_JOB_VALID_HOURS,
    Job,
    State,
)

if t.TYPE_CHECKING:
    from types import FrameType

    from sqlalchemy.orm import Session


class TestJob:
    def sample_job(self, payload=None):
        return Job(
            job_name="meltano:sample-elt",
            state=State.IDLE,
            payload=payload or {},
        )

    def test_save(self, session) -> None:
        subject = self.sample_job().save(session)

        assert subject.id > 0

    def test_load(self, session) -> None:
        for key in range(10):
            session.add(self.sample_job({"key": key}))

        subjects = session.query(Job).filter_by(job_name="meltano:sample-elt")

        assert len(subjects.all()) == 10
        session.rollback()

    def test_transit(self, session) -> None:
        subject = self.sample_job().save(session)

        transition = subject.transit(State.RUNNING)
        assert transition == (State.IDLE, State.RUNNING)
        subject.started_at = datetime.now(timezone.utc)

        transition = subject.transit(State.SUCCESS)
        assert transition == (State.RUNNING, State.SUCCESS)
        subject.ended_at = datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_run(self, session) -> None:
        subject = self.sample_job().save(session)

        # A successful run will mark the subject as SUCCESS and set the `ended_at`
        async with subject.run(session):
            assert subject.state is State.RUNNING
            assert subject.ended_at is None

            await asyncio.sleep(1)
            original_heartbeat = subject.last_heartbeat_at
            assert original_heartbeat is not None

            # Heartbeat is recorded every second
            await asyncio.sleep(2)
            assert subject.last_heartbeat_at > original_heartbeat

            # Yield to give heartbeat another chance to be updated
            await asyncio.sleep(0)

        assert subject.state is State.SUCCESS
        assert subject.ended_at is not None

        # Allow one additional second of delay:
        assert subject.ended_at - subject.last_heartbeat_at < timedelta(seconds=2)

    @pytest.mark.asyncio
    async def test_run_failed(self, session) -> None:
        # A failed run will mark the subject as FAILED an set the payload['error']
        subject = self.sample_job({"original_state": 1}).save(session)
        exception = Exception("This is a test.")

        with pytest.raises(Exception) as err:  # noqa: PT012, PT011
            async with subject.run(session):
                raise exception

            # raise the same exception
            assert err is exception

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "This is a test."

    @pytest.mark.asyncio
    async def test_run_interrupted(self, session) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/2842",
            )
        subject = self.sample_job({"original_state": 1}).save(session)

        # Install a signal handler that raises KeyboardInterrupt
        def sigint_handler(signum: int, frame: FrameType) -> None:  # noqa: ARG001
            raise KeyboardInterrupt

        original_handler = signal.signal(signal.SIGINT, sigint_handler)
        try:
            with pytest.raises(KeyboardInterrupt):
                async with subject.run(session):
                    signal.raise_signal(signal.SIGINT)
        finally:
            signal.signal(signal.SIGINT, original_handler)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was interrupted"

    @pytest.mark.asyncio
    async def test_run_terminated(self, session) -> None:
        if platform.system() == "Windows":
            pytest.xfail(
                "Fails on Windows: https://github.com/meltano/meltano/issues/2842",
            )
        subject = self.sample_job({"original_state": 1}).save(session)

        with pytest.raises(SystemExit):
            async with subject.run(session):
                signal.raise_signal(signal.SIGTERM)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was terminated"

    def test_run_id(self, session) -> None:
        job = Job()
        run_id = job.run_id
        assert isinstance(run_id, uuid.UUID)

        job.save(session)
        assert job.run_id == run_id

    def test_run_id_is_uuidv7(self, session) -> None:
        """Test that job run_id uses UUIDv7 format."""
        import time

        # Create two jobs with a small time gap
        job1 = Job()
        time.sleep(0.001)  # Wait 1ms to ensure different timestamps
        job2 = Job()

        # Both should have UUIDv7 version
        assert job1.run_id.version == 7
        assert job2.run_id.version == 7

        # They should be time-ordered (lexicographically sortable)
        assert str(job1.run_id) < str(job2.run_id)

        # Save and verify UUIDs persist correctly
        job1.save(session)
        job2.save(session)

        assert job1.run_id.version == 7
        assert job2.run_id.version == 7
        assert str(job1.run_id) < str(job2.run_id)

    def test_legacy_uuidv4_run_id(self, session: Session) -> None:
        """Test that a Job with a legacy UUIDv4 run_id is processed correctly."""
        legacy_run_id = uuid.uuid4()  # Simulate a legacy UUIDv4
        job = Job(run_id=legacy_run_id)
        job.save(session)

        # Reload the job from the database
        loaded_job = session.query(Job).filter_by(run_id=legacy_run_id).one()
        assert loaded_job.run_id == legacy_run_id
        assert isinstance(loaded_job.run_id, uuid.UUID)
        assert loaded_job.run_id.version == 4

    def test_is_stale(self) -> None:
        job = Job()

        # Idle jobs are not stale
        assert not job.is_stale()

        # Jobs that were just started are not stale
        job.start()
        assert not job.is_stale()

        # Jobs started more than 25 hours ago without a heartbeat are stale
        job.last_heartbeat_at = None
        offset = timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS + 1)
        job.started_at = datetime.now(timezone.utc) - offset
        assert job.is_stale()

        # Jobs with a recent heartbeat are not stale
        job._heartbeat()
        assert not job.is_stale()

        # Jobs without a heartbeat for 5 minutes are stale
        offset = timedelta(minutes=HEARTBEAT_VALID_MINUTES + 1)
        job.last_heartbeat_at = datetime.now(timezone.utc) - offset
        assert job.is_stale()

        # Completed jobs are not stale
        job.success()
        assert not job.is_stale()

    def test_fail_stale(self) -> None:
        job = Job()

        # Leaves a job that isn't stale alone
        assert not job.fail_stale()
        assert not job.has_error()

        # Fails a stale job without a heartbeat
        job.start()
        job.last_heartbeat_at = None
        offset = timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS + 1)
        job.started_at = datetime.now(timezone.utc) - offset

        assert job.fail_stale()
        assert job.has_error()
        assert "24 hours" in job.payload["error"]

        # Doesn't fail a job that's already failed
        assert not job.fail_stale()

        # Fails a stale job with a heartbeat
        job = Job()
        job.start()
        offset = timedelta(minutes=HEARTBEAT_VALID_MINUTES + 1)
        job.last_heartbeat_at = datetime.now(timezone.utc) - offset

        assert job.fail_stale()
        assert job.has_error()
        assert "5 minutes" in job.payload["error"]
