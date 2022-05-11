"""meltano tasks/jobs (not state related jobs)."""
from collections.abc import Iterable
from typing import List, TypeVar, Union

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical

T = TypeVar("T")  # noqa: WPS111


def _flatten(items):
    for el in items:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from _flatten(el)
        else:
            yield el


class TaskSets(NameEq, Canonical):
    """A job is a named entity that holds one or more Task's that can be executed by meltano."""

    def __init__(self, name: str, tasks: List[dict]):
        """Initialize a TaskSets.

        Args:
            name: The name of the job.
            tasks: The tasks that associated with this job.
        """
        super().__init__()

        self.name = name
        self.tasks = tasks

    def _squash(self, preserve_sets: bool = False) -> Union[str, List[str]]:
        """Squash the job's tasks into invocable string representations, suitable for passing as a cli argument.

        Args:
            preserve_sets: Whether to preserve the defined task sets to allow for fine grained executions.

        Returns:
            str: The squashed CLI argument.
        """
        if preserve_sets:
            flattened = []
            for task in self.tasks:
                if isinstance(task, Iterable) and not isinstance(task, (str, bytes)):
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
    def squashed_sets(self) -> List[str]:
        """Squash the job's tasks into discrete string representations, suitable for passing as a cli arguments.

        Returns:
            The squashed CLI arguments.
        """
        return self._squash(preserve_sets=True)
