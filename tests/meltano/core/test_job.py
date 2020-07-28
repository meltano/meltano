import sys
import pytest
import uuid
import psutil
import signal
from datetime import datetime
from unittest import mock

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

    def test_run(self, session):
        subject = self.sample_job().save(session)

        # A successful run will mark the subject as SUCCESS and set the `ended_at`
        with subject.run(session):
            assert subject.state is State.RUNNING
            assert subject.ended_at is None

        assert subject.state is State.SUCCESS
        assert subject.ended_at is not None

    def test_run_failed(self, session):
        # A failed run will mark the subject as FAILED an set the payload['error']
        subject = self.sample_job({"original_state": 1}).save(session)
        exception = Exception("This is a test.")

        with pytest.raises(Exception) as e:
            with subject.run(session):
                raise exception

            # raise the same exception
            assert e is exception

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "This is a test."

    def test_run_interrupted(self, session):
        subject = self.sample_job({"original_state": 1}).save(session)

        with pytest.raises(KeyboardInterrupt) as e:
            with subject.run(session):
                psutil.Process().send_signal(signal.SIGINT)

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "KeyboardInterrupt()"

    def test_run_terminated(self, session):
        subject = self.sample_job({"original_state": 1}).save(session)
        exception = Exception("Terminated")

        with pytest.raises(Exception) as er:
            with mock.patch.object(sys, "exit", side_effect=exception) as exit_mock:
                with subject.run(session):
                    psutil.Process().terminate()

                exit_mock.assert_called_once_with(143)

            assert e is exception

        assert subject.state is State.FAIL
        assert subject.ended_at is not None
        assert subject.payload["original_state"] == 1
        assert subject.payload["error"] == "The process was terminated"

    def test_run_id(self, session):
        expected_uuid = uuid.uuid4()
        job = Job()

        with mock.patch("uuid.uuid4", return_value=expected_uuid):
            assert job.run_id is None
            job.save(session)

            assert isinstance(job.run_id, uuid.UUID)
