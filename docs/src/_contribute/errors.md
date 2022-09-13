---
title: Custom errors
description: Creating custom exceptions and errors for the Meltano codebase.
layout: doc
weight: 10
---

This section describes how to create custom exception classes for Meltano.

## Creating a custom exception

_All_ new custom exceptions must inherit from `meltano.core.error.MeltanoError` or one of its subclasses. The subclass declaration takes the optional

The subclassed exception has to be instantiated with a required `reason` argument, which is a string describing the error, as well as the optional `instruction` argument that can be used to provide additional next troubleshooting steps to the user.

```python
from meltano.core.error import MeltanoError


class ScheduleDoesNotExistError(MeltanoError):
    """Occurs when a schedule does not exist."""

    def __init__(self, name: str):
        """Initialize the exception.

        Args:
            name: The name of the schedule that does not exist.

        """
        self.name = name

        reason = f"Schedule '{self.name}' does not exist"
        instruction = "Use `meltano schedule add` to add a schedule"
        super().__init__(reason, instruction)
```
