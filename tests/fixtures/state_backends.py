from __future__ import annotations

from meltano.core.state_store import StateStoreManager


class DummyStateStoreManager(StateStoreManager):
    label: str = "Dummy state store manager"

    def __init__(self, **kwargs): ...

    def set(self, state): ...

    def get(self, state_id): ...

    def clear(self, state_id): ...

    def get_state_ids(self, pattern=None):  # noqa: ARG002
        return ()  # pragma: no cover

    def acquire_lock(self, state_id): ...
