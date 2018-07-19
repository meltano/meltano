import pytest

from meltano.common.job import Job, State
from datetime import datetime

def sample_job(payload={}):
    return Job(elt_uri='elt://bizops/sample-elt',
               state=State.IDLE,
               payload=payload)


def test_save(session):
    job = sample_job()
    session.add(job)
    session.commit()

    assert(job.id > 0)


def test_save_raw(db):
    job = sample_job()
    Job.save(job)

    assert(job.id > 0)


def test_load(session):
    [session.add(sample_job({'key': i})) for i in range(0, 10)]
    session.commit()

    jobs = session.query(Job).filter_by(elt_uri='elt://bizops/sample-elt')

    assert(len(jobs.all()) == 10)


def test_transit(session):
    j = sample_job()

    transition = j.transit(State.RUNNING)
    assert(transition == (State.IDLE, State.RUNNING))
    j.started_at = datetime.utcnow()

    transition = j.transit(State.SUCCESS)
    assert(transition == (State.RUNNING, State.SUCCESS))
    j.ended_at = datetime.utcnow()

    session.add(j)
