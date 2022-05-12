import pytest

from meltano.core.task_sets import TaskSets
from meltano.core.task_sets_service import (
    JobAlreadyExistsError,
    JobNotFoundError,
    TaskSetsService,
)


@pytest.fixture(scope="session")
def create_task_set():
    def make(name):
        return TaskSets(name=name, tasks=["tap-mock target-mock"])

    return make


class TestTaskSetsService:
    @pytest.fixture()
    def subject(self, task_sets_service):
        return task_sets_service

    def test_add(self, subject: TaskSetsService, create_task_set):
        count = 3
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        assert subject.list() == jobs

        # verify that we can not add a job with the same name
        with pytest.raises(JobAlreadyExistsError):
            subject.add(jobs[0])

    def test_remove(self, subject: TaskSetsService, create_task_set):
        count = 3
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        subject.remove(jobs[0].name)
        assert subject.list() == jobs[1:]
        assert subject.exists(jobs[0].name) is False

        # verify that we can not remove a job that does not exist
        with pytest.raises(JobNotFoundError):
            subject.remove(jobs[0].name)

    def test_get(self, subject: TaskSetsService, create_task_set):
        count = 3
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        assert subject.get(jobs[0].name) == jobs[0]

        # verify that we can not get a job that does not exist
        with pytest.raises(JobNotFoundError):
            subject.get("non-existent")

    def test_list(self, subject: TaskSetsService, create_task_set):
        # empty case

        empty = []
        assert subject.list() == empty

        count = 3
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        assert subject.list() == jobs

    def test_exists(self, subject: TaskSetsService, create_task_set):
        count = 3
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        for job in jobs:
            assert subject.exists(job.name)

        assert not subject.exists("non-existent")
