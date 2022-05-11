"""Service for managing task sets (aka jobs)."""
from typing import List

import structlog

from meltano.core.block.parser import BlockParser, validate_block_sets
from meltano.core.project import Project

from .task_sets import TaskSets

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


class JobTaskInvalidError(Exception):
    """Occurs when a task in a TaskSet (aka job) is invalid."""

    def __init__(self, name: str, error: str = None):
        """Initialize a JobTaskInvalidError.

        Args:
            name: Name of the TaskSet (aka job) that was invalid.
            error: Error message.
        """
        self.name = name
        if error:
            super().__init__(f"Job '{name}' has invalid task: {error}")
        else:
            super().__init__(f"Job '{name}' has invalid task.")


class TaskSetsService:
    """A service for managing project TaskSets."""

    def __init__(self, project: Project):
        """Initialize a TaskSetsService.

        Args:
            project: The active project.
        """
        self.project = project

    def add(self, name: str, tasks: List[List[str]]) -> None:
        """Add a TaskSet to the project.

        Args:
            name: The name of the TaskSet.
            tasks: The tasks that should be associated with the TaskSet.

        Raises:
            JobAlreadyExistsError: When a TaskSet with the same name already exists.
            JobTaskInvalidError: When the tasks in a job are not valid.
        """
        if self.exists(name):
            raise JobAlreadyExistsError(name)
        with self.project.meltano_update() as meltano:
            for blocks in tasks:
                try:
                    parser = BlockParser(logger, self.project, blocks)
                    parsed_blocks = list(parser.find_blocks(0))
                except Exception as err:
                    raise JobTaskInvalidError(name, err) from err
                if not validate_block_sets(logger, parsed_blocks):
                    raise JobTaskInvalidError(name, "Block set validation failed.")
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
