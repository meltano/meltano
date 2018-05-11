import pytest

from elt.job import Job, State


def test_save(dbcursor):
    j = Job('elt://bizops/sample-elt',
            payload={
                'key': "value"
            })

    assert(Job.save(dbcursor, j))



def test_load(dbcursor):
    for i in range(0, 10):
        j = Job('elt://bizops/sample-elt',
                state=State.IDLE,
                payload={'key': str(i)})
        Job.save(dbcursor, j)

    jobs = Job.for_elt(dbcursor, 'elt://bizops/sample-elt')
    print(jobs)
    assert(len(jobs) == 10)
