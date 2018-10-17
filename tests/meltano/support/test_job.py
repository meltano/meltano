import pytest

from meltano.support.job import Job, State
from datetime import datetime


def sample_job(payload={}):
    return Job(elt_uri="elt://bizops/sample-elt", state=State.IDLE, payload=payload)


def test_save(session):
    subject = sample_job().save()

    assert subject.id > 0


def test_load(session):
    [session.add(sample_job({"key": i})) for i in range(0, 10)]

    subjects = session.query(Job).filter_by(elt_uri="elt://bizops/sample-elt")

    assert len(subjects.all()) == 10
    session.rollback()


def test_transit(session):
    subject = sample_job().save()

    transition = subject.transit(State.RUNNING)
    assert transition == (State.IDLE, State.RUNNING)
    subject.started_at = datetime.utcnow()

    transition = subject.transit(State.SUCCESS)
    assert transition == (State.RUNNING, State.SUCCESS)
    subject.ended_at = datetime.utcnow()


def test_run(session):
    subject = sample_job().save()

    # A successful run will mark the subject as SUCCESS and set the `ended_at`
    with subject.run():
        assert subject.state == State.RUNNING
        assert subject.ended_at is None

    assert subject.state == State.SUCCESS
    assert subject.ended_at is not None


def test_run_failed(session):
    # A failed run will mark the subject as FAILED an set the payload['error']
    subject = sample_job().save()
    exception = Exception("This is a test.")

    with pytest.raises(Exception) as e:
        with subject.run():
            raise exception

        # raise the same exception
        assert e is exception

    assert subject.state == State.FAIL
    assert subject.ended_at is not None
    assert subject.payload["error"] == "This is a test."


def test_this(session):
    assert session
