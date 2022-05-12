"""meltano tasks/jobs (not state related jobs)."""
from collections.abc import Iterable
from typing import List, TypeVar, Union

import structlog

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical

logger = structlog.getLogger(__name__)


T = TypeVar("T")  # noqa: WPS111


def _flatten(items):
    for el in items:
        if isinstance(el, Iterable) and not isinstance(el, str):
            yield from _flatten(el)
        else:
            yield el


class TaskSets(NameEq, Canonical):
    """A job is a named entity that holds one or more Task's that can be executed by meltano."""

    def __init__(self, name: str, tasks: List[List[str]]):
        """Initialize a TaskSets.

        Args:
            name: The name of the job.
            tasks: The tasks that associated with this job.
        """
        super().__init__()

        self.name = name
        self.tasks = tasks

    def _squash(self, preserve_top_level: bool = False) -> Union[str, List[str]]:
        """Squash the job's tasks into invocable string representations, suitable for passing as a cli argument.

        Args:
            preserve_top_level: Whether to preserve the defined top level task list to allow for fine grained executions.

        Returns:
            str: The squashed CLI argument.
        """
        if preserve_top_level:
            flattened = []
            for task in self.tasks:
                if isinstance(task, Iterable) and not isinstance(task, str):
                    flattened.extend(list(_flatten(task)))
                else:
                    flattened.append(task)
            return flattened

        return " ".join(_flatten(self.tasks))

    @property
    def squashed(self) -> str:
        """Squash the job's tasks into a singe invocable string representations, suitable for passing as a cli argument.

        Returns:
            The squashed CLI argument.
        """
        return self._squash()

    @property
    def squashed_per_set(self) -> List[str]:
        """Squash the job's tasks into perk task string representations (preserving top level list hierarchy).

        Returns:
            The squashed CLI arguments.
        """
        return self._squash(preserve_top_level=True)


def tasks_from_str(name: str, tasks: str) -> TaskSets:  # noqa: WPS238
    """Create a TaskSets from a string representation of the tasks.

    The CLI supports both a single task representation as well as pseudo-task list of representations, so this function
    will handle either based on the presence of wrapping '[]' characters. We check if the str is grossly malformed i.e.
    has leading or trailing quotes, or unbalanced brackets, or comma without list convention, but make no other
    attempts to validate the string.

    Example:
        tasks_from_str("my_job", "tap target dbt:run") # a single task
        tasks_from_str("my_job", '[tap mapper target, dbt:run, tap2 target2]) # three tasks

    Args:
        name: The name of the TaskSet.
        tasks: The tasks that should be associated with the TaskSet.

    Returns:
        TaskSets obj generated from the string representation.

    Raises:
        ValueError: If the string representation appears to be obviously malformed
    """
    if tasks.strip("\"' ") != tasks:
        raise ValueError(f"Invalid tasks string: {tasks}")

    if tasks.endswith("]") and not tasks.startswith("["):
        raise ValueError(f"Invalid tasks string, missing leading '[': {tasks}")

    if tasks.startswith("[") and not tasks.endswith("]"):
        raise ValueError(f"Invalid tasks string, missing trailing ']': {tasks}")

    if tasks.startswith("[") and tasks.endswith("]"):
        parsed = [task.strip(" ") for task in tasks[1:-1].split(",") if task]
        return TaskSets(name, parsed)

    if "," in tasks:
        raise ValueError(f"Invalid tasks string, non list contains comma: {tasks}")

    return TaskSets(name, [tasks])
