---
title: Custom errors
description: Creating custom exceptions and errors for the Meltano codebase.
layout: doc
sidebar_position: 10
---

This section describes how to create custom exception classes for Meltano.

## Creating a custom exception

_All_ new custom exceptions must inherit from `meltano.core.error.MeltanoError` or one of its subclasses.

The `meltano.core.error.MeltanoError` initializer takes in a `reason` argument, which is a string describing the error, as well as the optional `instruction` argument that can be used to provide additional troubleshooting steps for the user.

```python
from meltano.core.error import MeltanoError


class StoreNotSupportedError(MeltanoError):
    """Error raised when write actions are performed on a Store that is not writable."""

    def __init__(
        self,
        reason: str | Exception = "Store is not supported",
        **kwds: t.Any,
    ) -> None:
        """Instantiate the error."""
        super().__init__(reason, **kwds)
```
