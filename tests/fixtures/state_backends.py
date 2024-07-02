from __future__ import annotations

from meltano.core.state_store import StateStoreManager


class DummyStateStoreManager(StateStoreManager):
    label: str = "Dummy state store manager"

    def __init__(self, **kwargs): ...  # noqa: WPS428

    def set(self, state): ...  # noqa: WPS428

    def get(self, state_id): ...  # noqa: WPS428

    def clear(self, state_id): ...  # noqa: WPS428

    def get_state_ids(self, _pattern=None):
        return ()  # pragma: no cover

    def acquire_lock(self, state_id): ...  # noqa: WPS428
