import pytest

from elt.job import Job, State
from datetime import datetime

def sample_job(payload={}):
    return Job('elt://bizops/sample-elt',
               state=State.IDLE,
               payload=payload)


def test_save(db):
    assert(Job.save(sample_job()))


def test_load(db):
    for i in range(0, 10):
        Job.save(sample_job({'key': i}))

    jobs = Job.for_elt('elt://bizops/sample-elt')
    [print(x.__dict__()) for x in jobs]
    assert(len(jobs) == 10)


def test_transit(db):
    j = sample_job()

    transition = j.transit(State.RUNNING)
    assert(transition == (State.IDLE, State.RUNNING))
    j.started_at = datetime.utcnow()

    transition = j.transit(State.SUCCESS)
    assert(transition == (State.RUNNING, State.SUCCESS))
    j.ended_at = datetime.utcnow()

    Job.save(j)
