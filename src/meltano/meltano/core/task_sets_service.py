"""Service for managing task sets (aka jobs)."""
from __future__ import annotations

import structlog

from meltano.core.project import Project
from meltano.core.task_sets import TaskSets

logger = structlog.getLogger(__name__)


class JobAlreadyExistsError(Exception):
    """Occurs when a TaskSet (aka job) already exists."""

    def __init__(self, name: str):
        """Initialize a JobAlreadyExistsError.

        Args:
            name: Name of the TaskSet (aka job) that already exists.
        """
        self.name = name


class JobNotFoundError(Exception):
    """Occurs when a TaskSet (aka job) does not exists."""

    def __init__(self, name: str):
        """Initialize a JobNotFoundError.

        Args:
            name: Name of the TaskSet (aka job) that wasn't found.
        """
        self.name = name
        super().__init__(f"Job '{name}' was not found.")


class TaskSetsService:
    """A service for managing project TaskSets."""

    def __init__(self, project: Project):
        """Initialize a TaskSetsService.

        Args:
            project: The active project.
        """
        self.project = project

    def add(self, task_sets: TaskSets) -> None:
        """Add a TaskSet to the project.

        Args:
            task_sets: The TaskSets to add.

        Raises:
            JobAlreadyExistsError: When a TaskSet with the same name already exists.
        """
        if self.exists(task_sets.name):
            raise JobAlreadyExistsError(task_sets.name)

        with self.project.meltano_update() as meltano:
            logger.debug("adding job", name=task_sets.name, tasks=task_sets.tasks)
            meltano.jobs.append(task_sets)

    def remove(self, name: str) -> TaskSets:
        """Remove a TaskSet from the project.

        Args:
            name: The name of the TaskSet to remove.

        Returns:
            The removed TaskSet.

        Raises:
            JobNotFoundError: If the TaskSet with the given name does not exist.
        """
        for job in self.list():
            if job.name == name:
                with self.project.meltano_update() as meltano:
                    logger.debug("removing job", name=job.name)
                    meltano.jobs.remove(job)
                return job
        raise JobNotFoundError(name)

    def update(self, task_sets: TaskSets) -> None:
        """Update a tasks.

        Args:
            task_sets: The TaskSets to update.

        Raises:
            JobNotFoundError: If the TaskSet with the given name does not exist.
        """
        for idx, job in enumerate(self.list()):
            if job.name == task_sets.name:
                with self.project.meltano_update() as meltano:
                    logger.debug("updating job", name=job.name)
                    meltano.jobs[idx].tasks = task_sets.tasks
                return
        raise JobNotFoundError(task_sets.name)

    def get(self, name: str) -> TaskSets:
        """Get a TaskSet by name.

        Args:
            name: The name of the TaskSet.

        Returns:
            The TaskSet with the given name.

        Raises:
            JobNotFoundError: If the TaskSet with the given name does not exist.
        """
        for job in self.project.meltano.jobs:
            if job.name == name:
                return job
        raise JobNotFoundError(name)

    def list(self) -> list[TaskSets]:  # noqa: WPS125
        """List all TaskSets in the project.

        Returns:
            A list of all TaskSets in the project.
        """
        return self.project.meltano.jobs.copy()

    def exists(self, name: str) -> bool:
        """Check if a TaskSet with the given name exists.

        Args:
            name: The name of the TaskSet.

        Returns:
            True if the TaskSet with the given name exists, False otherwise.
        """
        try:
            self.get(name)
        except JobNotFoundError:
            return False
        return True
