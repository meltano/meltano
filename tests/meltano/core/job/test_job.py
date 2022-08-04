from __future__ import annotations

import asyncio
import platform
import signal
import uuid
from datetime import datetime, timedelta

import psutil
import pytest

from meltano.core.job.job import (
    HEARTBEAT_VALID_MINUTES,
    HEARTBEATLESS_JOB_VALID_HOURS,
    Job,
    State,
)


class TestJob:
    def sample_job(self, payload=None):
        return Job(
            job_name="meltano:sample-elt", state=State.IDLE, payload=payload or {}
        )

    def test_save(self, session):
        subject = self.sample_job().save(session)

        assert subject.id > 0

    def test_load(self, session):
        for key in range(0, 10):
            session.add(self.sample_job({"key": key}))

        subjects = session.query(Job).filter_by(job_name="meltano:sample-elt")

        assert len(subjects.all()) == 10
        session.rollback()

    def test_transit(self, session):
        subject = self.sample_job().save(session)

        transition = subject.transit(State.RUNNING)
        assert transition == (State.IDLE, State.RUNNING)
        subject.started_at = datetime.utcnow()

        transition = subject.transit(State.SUCCESS)
        assert transition == (State.RUNNING, State.SUCCESS)
        subject.ended_at = datetime.utcnow()

    @pytest.mark.asyncio
    async def test_run(self, session):
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
    async def test_run_failed(self, session):
        # A failed run will mark the subject as FAILED an set the payload['error']
        subject = self.sample_job({"original_state": 1}).save(session)
        exception = Exception("This is a test.")

        with pytest.raises(Exception) as err:
            async with subject.run(session):
                raise exception

            # raise the same exception
            assert err is exception

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "This is a test."

    @pytest.mark.asyncio
    async def test_run_interrupted(self, session):

        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/2842"
            )
        subject = self.sample_job({"original_state": 1}).save(session)
        with pytest.raises(KeyboardInterrupt):
            async with subject.run(session):
                send_signal(signal.SIGINT)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was interrupted"

    @pytest.mark.asyncio
    async def test_run_terminated(self, session):

        if platform.system() == "Windows":
            pytest.xfail(
                "Doesn't pass on windows, this is currently being tracked here https://github.com/meltano/meltano/issues/2842"
            )
        subject = self.sample_job({"original_state": 1}).save(session)

        with pytest.raises(SystemExit):
            async with subject.run(session):
                send_signal(signal.SIGTERM)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was terminated"

    def test_run_id(self, session):
        job = Job()
        run_id = job.run_id
        assert isinstance(run_id, uuid.UUID)

        job.save(session)
        assert job.run_id == run_id

    def test_is_stale(self):
        job = Job()

        # Idle jobs are not stale
        assert not job.is_stale()

        # Jobs that were just started are not stale
        job.start()
        assert not job.is_stale()

        # Jobs started more than 25 hours ago without a heartbeat are stale
        offset = timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS + 1)
        job.started_at = datetime.utcnow() - offset
        assert job.is_stale()

        # Jobs with a recent heartbeat are not stale
        job._heartbeat()
        assert not job.is_stale()

        # Jobs without a heartbeat for 5 minutes are stale
        offset = timedelta(minutes=HEARTBEAT_VALID_MINUTES + 1)
        job.last_heartbeat_at = datetime.utcnow() - offset
        assert job.is_stale()

        # Completed jobs are not stale
        job.success()
        assert not job.is_stale()

    def test_fail_stale(self):
        job = Job()

        # Leaves a job that isn't stale alone
        assert not job.fail_stale()
        assert not job.has_error()

        # Fails a stale job without a heartbeat
        job.start()
        offset = timedelta(hours=HEARTBEATLESS_JOB_VALID_HOURS + 1)
        job.started_at = datetime.utcnow() - offset

        assert job.fail_stale()
        assert job.has_error()
        assert "24 hours" in job.payload["error"]

        # Doesn't fail a job that's already failed
        assert not job.fail_stale()

        # Fails a stale job with a heartbeat
        job = Job()
        job.start()
        offset = timedelta(minutes=HEARTBEAT_VALID_MINUTES + 1)
        job.last_heartbeat_at = datetime.utcnow() - offset

        assert job.fail_stale()
        assert job.has_error()
        assert "5 minutes" in job.payload["error"]


def send_signal(signal: int):
    if platform.system() == "Windows":
        # Replace once Python 3.7 has been dropped see https://github.com/meltano/meltano/issues/6223
        import ctypes

        ucrtbase = ctypes.CDLL("ucrtbase")
        c_raise = ucrtbase["raise"]
        c_raise(signal)
    else:
        psutil.Process().send_signal(signal)
