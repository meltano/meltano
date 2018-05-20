import pytest

from elt.db import DB
from elt.job import Job, State
from datetime import datetime

def sample_job(payload={}):
    return Job(elt_uri='elt://bizops/sample-elt',
               state=State.IDLE,
               payload=payload)


def test_save(db):
    job = sample_job()
    Job.save(job)
    assert(job)


def test_load(db):
    with DB.session() as session:
        [session.add(sample_job({'key': i})) for i in range(0, 10)]
        import pdb; pdb.set_trace()
        session.flush()

    import pdb; pdb.set_trace()
    with DB.session() as s:
        jobs = s.query(Job).filter_by(elt_uri='elt://bizops/sample-elt')

    assert(len(jobs.all()) == 10)


def test_transit(db):
    j = sample_job()

    transition = j.transit(State.RUNNING)
    assert(transition == (State.IDLE, State.RUNNING))
    j.started_at = datetime.utcnow()

    transition = j.transit(State.SUCCESS)
    assert(transition == (State.RUNNING, State.SUCCESS))
    j.ended_at = datetime.utcnow()

    Job.save(j)
