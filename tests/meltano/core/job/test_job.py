import asyncio
import signal
import uuid
from datetime import datetime, timedelta

import psutil
import pytest
from meltano.core.job import Job, State


class TestJob:
    def sample_job(self, payload={}):
        return Job(job_id="meltano:sample-elt", state=State.IDLE, payload=payload)

    def test_save(self, session):
        subject = self.sample_job().save(session)

        assert subject.id > 0

    def test_load(self, session):
        [session.add(self.sample_job({"key": i})) for i in range(0, 10)]

        subjects = session.query(Job).filter_by(job_id="meltano:sample-elt")

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
        subject = self.sample_job({"original_state": 1}).save(session)

        with pytest.raises(KeyboardInterrupt):
            async with subject.run(session):
                psutil.Process().send_signal(signal.SIGINT)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was interrupted"

    @pytest.mark.asyncio
    async def test_run_terminated(self, session):
        subject = self.sample_job({"original_state": 1}).save(session)

        with pytest.raises(SystemExit):
            async with subject.run(session):
                psutil.Process().terminate()

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
