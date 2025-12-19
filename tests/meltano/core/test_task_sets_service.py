from __future__ import annotations

import typing as t

import pytest

from meltano.core.task_sets import TaskSets
from meltano.core.task_sets_service import JobAlreadyExistsError, JobNotFoundError

if t.TYPE_CHECKING:
    from meltano.core.task_sets_service import TaskSetsService


@pytest.fixture(scope="session")
def create_task_set():
    def make(name):
        return TaskSets(name=name, tasks=["tap-mock target-mock"])

    return make


class TestTaskSetsService:
    @pytest.fixture
    def subject(self, task_sets_service):
        return task_sets_service

    @pytest.mark.order(0)
    def test_add(self, subject: TaskSetsService, create_task_set) -> None:
        count = 10
        jobs = [create_task_set(f"test_job_{idx}") for idx in range(count)]

        for job in jobs:
            subject.add(job)

        assert subject.list_task_sets() == jobs

        # verify that we can not add a job with the same name
        with pytest.raises(JobAlreadyExistsError):
            subject.add(jobs[0])

    def test_update(self, subject: TaskSetsService, create_task_set) -> None:
        job = subject.list_task_sets()[0]
        job.tasks = ["tap-mock target-mock updated:addition"]
        subject.update(job)

        assert subject.get(job.name).tasks == ["tap-mock target-mock updated:addition"]

        nonexistent = create_task_set("does-not-exist")
        with pytest.raises(JobNotFoundError):
            subject.update(nonexistent)

    @pytest.mark.usefixtures("create_task_set")
    def test_remove(self, subject: TaskSetsService) -> None:
        jobs = subject.list_task_sets()
        subject.remove(jobs[0].name)
        assert subject.list_task_sets() == jobs[1:]
        assert subject.exists(jobs[0].name) is False

        # verify that we can not remove a job that does not exist
        with pytest.raises(JobNotFoundError):
            subject.remove(jobs[0].name)

    @pytest.mark.usefixtures("create_task_set")
    def test_get(self, subject: TaskSetsService) -> None:
        jobs = subject.list_task_sets()

        assert subject.get(jobs[0].name) == jobs[0]

        # verify that we can not get a job that does not exist
        with pytest.raises(JobNotFoundError):
            subject.get("non-existent")

    @pytest.mark.usefixtures("create_task_set")
    def test_exists(self, subject: TaskSetsService) -> None:
        job = subject.list_task_sets()[0]
        assert subject.exists(job.name)
        assert not subject.exists("non-existent")

    def test_list(self, subject: TaskSetsService, create_task_set) -> None:
        expected_jobs = [create_task_set(f"test_list_{idx}") for idx in range(3)]

        for job in expected_jobs:
            subject.add(job)

        result = subject.list_task_sets()

        for job in expected_jobs:
            assert job in result
