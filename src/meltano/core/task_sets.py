"""meltano tasks/jobs (not state related jobs)."""
from __future__ import annotations

from collections.abc import Iterable

import structlog
import yaml
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical

logger = structlog.getLogger(__name__)


TASKS_JSON_SCHEMA = {
    "oneOf": [
        {"type": "string"},
        {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "string"}},
                ]
            },
        },
    ],
}


class InvalidTasksError(Exception):
    """Raised when a yaml str cannot be parsed into a valid tasks list."""

    def __init__(self, name: str, message: str):
        """Initialize a InvalidTasksError.

        Args:
            name: Name of the TaskSet that was invalid.
            message: The message describing the error.
        """
        self.name = name
        super().__init__(f"Job '{name}' has invalid tasks. {message}")


def _flat_split(items):
    for el in items:
        if isinstance(el, Iterable) and not isinstance(el, str):
            yield from _flat_split(el)
        else:
            if " " in el:
                yield from _flat_split(el.split(" "))
            else:
                yield el


class TaskSets(NameEq, Canonical):
    """A job is a named entity that holds one or more Task's that can be executed by meltano."""

    def __init__(self, name: str, tasks: list[str] | list[list[str]]):
        """Initialize a TaskSets.

        Args:
            name: The name of the job.
            tasks: The tasks that associated with this job.
        """
        super().__init__()

        self.name = name
        self.tasks = tasks

    def _as_args(self, preserve_top_level: bool = False) -> list[str] | list[list[str]]:
        """Convert the job's tasks into invocable representations, suitable for passing as a cli args or block names.

        Args:
            preserve_top_level: Whether to preserve the defined top level task list to allow for fine-grained executions.

        Returns:
            The run arguments.
        """
        if not preserve_top_level:
            return list(_flat_split(self.tasks))

        flattened = []
        for task in self.tasks:
            if isinstance(task, str):
                flattened.append(task.split(" "))
            else:
                flattened.append(list(_flat_split(task)))
        return flattened

    @property
    def flat_args(self) -> list[str]:
        """Convert job's tasks to a single invocable representations. For passing as a cli argument or as block names.

        Example:
            TaskSets(name="foo", tasks=["tap target", "some:cmd"]).flat_args -> ["tap", "target", "some:cmd"]

        Returns:
            The run arguments.
        """
        return self._as_args()

    @property
    def flat_args_per_set(self) -> list[str] | list[list[str]]:
        """Convert the job's tasks into perk task representations (preserving top level list hierarchy).

        Example:
            TaskSets(name="foo", tasks=[["tap trgt"], ["some:cmd"]).flat_args_per_set -> [["tap", "trgt"], ["some:cmd"]]

        Returns:
            The per-task run arguments.
        """
        return self._as_args(preserve_top_level=True)


def tasks_from_yaml_str(name: str, yaml_str: str) -> TaskSets:
    """Create a TaskSets from a yaml string.

    The resulting object is validated against the TASKS_JSON_SCHEMA.

    Args:
        name: The name of the job.
        yaml_str: The yaml string.

    Returns:
        The TaskSets.

    Raises:
        InvalidTasksError: If the yaml string failed to parse or failed to validate against the TASKS_JSON_SCHEMA.
    """
    tasks = []
    try:
        tasks = yaml.safe_load(yaml_str)
    except yaml.parser.ParserError as yerr:
        raise InvalidTasksError(name, f"Failed to parse yaml '{yaml_str}': {yerr}")

    try:
        validate(instance=tasks, schema=TASKS_JSON_SCHEMA)
    except ValidationError as verr:
        raise InvalidTasksError(name, f"Failed to validate task schema: {verr}")

    # Handle the special case of a single task
    if isinstance(tasks, str):
        tasks = [tasks]

    return TaskSets(name=name, tasks=tasks)
