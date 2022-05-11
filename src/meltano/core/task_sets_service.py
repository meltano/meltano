"""Service for managing task sets (aka jobs)."""
from typing import List

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

    def add(self, name: str, tasks: TaskSets) -> None:
        """Add a TaskSet to the project.

        Args:
            name: The name of the TaskSet.
            tasks: The tasks that should be associated with the TaskSet.

        Raises:
            JobAlreadyExistsError: When a TaskSet with the same name already exists.
        """
        if self.exists(name):
            raise JobAlreadyExistsError(name)

        with self.project.meltano_update() as meltano:
            logger.debug("Adding job", name=name, tasks=tasks)
            meltano.jobs.append(TaskSets(name=name, tasks=tasks))

    def add_from_str(self, name: str, tasks: str) -> None:
        """Add a TaskSet to the project from a string representation of the tasks.

        Example:
            add_from_str("my_job", "tap target dbt:run") # a single task
            add_from_str("my_job", '[tap mapper target, dbt:run, tap2 target2]) # three tasks

        Args:
            name: The name of the TaskSet.
            tasks: The tasks that should be associated with the TaskSet.
        """
        if tasks.startswith("[") and tasks.endswith("]"):
            cleaned = [
                task.strip('"').strip(" ").split(" ")
                for task in tasks[1:-1].split(",")
                if task
            ]
            self.add(name, cleaned)
        else:
            self.add(name, tasks.split(" "))

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

    def list(self) -> List[TaskSets]:
        """List all TaskSets in the project.

        Returns:
            A list of all TaskSets in the project.
        """
        return self.project.meltano.jobs

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
