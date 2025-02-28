---
title: Custom State Backends
description: Learn how to create a custom state backend for Meltano.
layout: doc
sidebar_position: 20
---

To create a custom state backend for Meltano, you need to implement the `StateStoreManager` interface and any settings required to configure the backend.

```python
# my_state_manager/backend.py
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

    def get(self) -> MeltanoState | None:
        # Implement the logic to retrieve the state from your custom backend

    def clear(self) -> None:
        # Implement the logic to clear the state from your custom backend

    def get_state_ids(self) -> list[str]:
        # Implement the logic to retrieve the list of state IDs from your custom backend
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
