---
title: Custom State Backends
description: Learn how to create a custom state backend for Meltano.
layout: doc
sidebar_position: 20
---

Meltano's state backend system is highly extensible, allowing you to store pipeline state in virtually any system that can be a key-value store. This includes cloud data warehouses like Redshift and BigQuery or modern data stores like PostgreSQL or MongoDB.

To create a custom state backend, you need to implement the `StateStoreManager` interface and any settings required to configure the backend. This guide shows you how to build a custom state backend that can integrate with any storage system.

:::tip
Before building a custom state backend, check if one of the [built-in state backends](/concepts/state_backends) meets your needs. Meltano includes support for system databases, local filesystems, and major cloud storage providers.
:::

```python
# my_state_manager/backend.py
from contextlib import contextmanager
from urllib.parse import urlparse

from meltano.core.error import MeltanoError
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.state_store.base import MeltanoState, StateStoreManager


USERNAME = SettingDefinition(
    key="username",
    label="Username",
    kind=SettingKind.STRING,
    description="The username to use when connecting to the custom state manager",
)

PASSWORD = SettingDefinition(
    key="password",
    label="Password",
    kind=SettingKind.STRING,
    sensitive=True,
    description="The password to use when connecting to the custom state manager",
)


class MyStateManagerError(MeltanoError):
    pass


class MyStateManager(StateStoreManager):
    """My Custom State Manager"""

    label: str = "My Custom State Manager"

    def __init__(
        self,
        uri: str,
        *,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.uri = uri

        # Parse the URI to extract the connection details
        # Expecting `msm://<host>/<database>`, e.g. `msm://localhost/meltano`
        parsed = urlparse(uri)
        self.host = parsed.hostname
        self.database = parsed.path.lstrip("/")

        self.username = username or parsed.username

        if not self.username:
            raise MyStateManagerError("Username is required")

        self.password = password or parsed.password

        if not self.password:
            raise MyStateManagerError("Password is required")


    def set(self, state: MeltanoState) -> None:
        # Implement the logic to store the state in your custom backend
        ...

    def get(self, state_id: str) -> MeltanoState | None:
        # Implement the logic to retrieve the state from your custom backend
        ...

    def delete(self, state_id: str) -> None:
        # Implement the logic to delete the state for a given state ID
        ...

    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        # Implement the logic to retrieve the list of state IDs from
        # your custom backend, optionally filtered by a glob pattern
        ...

    @contextmanager
    def acquire_lock(self, state_id: str, *, retry_seconds: int = 1):
        # Implement the logic to acquire a lock for the given state ID.
        # This method should be a context manager that acquires the lock
        # and releases it when the context exits.
        yield

    def migrate(self) -> None:
        # Optionally implement migration logic for your custom backend.
        # This is called by `meltano upgrade` to perform any necessary
        # data migrations (e.g., fixing path prefixes, schema changes).
        # The default implementation is a no-op.
        ...
```

To let Meltano know about your custom state manager, you need to add the following configuration to your `pyproject.toml`:

```toml
[project.entry-points."meltano.settings"]
my_state_manager_username = "my_state_manager.backend:USERNAME"
my_state_manager_password = "my_state_manager.backend:PASSWORD"

[project.entry-points."meltano.state_backends"]
# These keys should match the expected scheme for URIs of
# the given type. E.g., filesystem state backends have a
# file://<path>/<to>/<state directory> URI
msm = "my_state_manager.backend:MyStateManager"
```

You can now use your custom state manager by installing it alongside Meltano:

```bash
uv tool install --with git+https://github.com/your-username/my-state-manager.git meltano
```
