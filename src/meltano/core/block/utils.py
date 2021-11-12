from asyncio import Task
from typing import List, Set


def all_done(tasks: List[Task], done: Set[Task]) -> bool:
    """Iterate through a task list checking if ALL tasks are in the done set."""
    for i in tasks:
        if i not in done:
            return False
    return True
