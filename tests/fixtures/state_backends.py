from __future__ import annotations

import fnmatch
import sys
import typing as t
from contextlib import contextmanager

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

from meltano.core.state_store import StateStoreManager

if t.TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from meltano.core.state_store.base import MeltanoState


class DummyStateStoreManager(StateStoreManager):
    label: str = "Dummy state store manager"

    def __init__(self, **kwargs): ...

    @override
    def set(self, state): ...

    @override
    def get(self, state_id): ...

    @override
    def delete(self, state_id): ...

    @override
    def get_state_ids(self, pattern=None):
        return ()  # pragma: no cover

    @override
    def acquire_lock(self, state_id): ...


class InMemoryStateStoreManager(StateStoreManager):
    """Minimal in-memory backend for testing the base-class get_all/set_all fallbacks.

    Does NOT override get_all or set_all — tests that use this class verify the
    default implementations in StateStoreManager.
    """

    label: str = "In-memory (test)"

    def __init__(self, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)
        self._store: dict[str, MeltanoState] = {}

    @override
    def set(self, state: MeltanoState) -> None:
        self._store[state.state_id] = state

    @override
    def get(self, state_id: str) -> MeltanoState | None:
        return self._store.get(state_id)

    @override
    def delete(self, state_id: str) -> None:
        self._store.pop(state_id, None)

    @override
    def get_state_ids(self, pattern: str | None = None) -> Iterable[str]:
        if pattern is None:
            return list(self._store)
        return [sid for sid in self._store if fnmatch.fnmatch(sid, pattern)]

    @override
    @contextmanager
    def acquire_lock(
        self,
        state_id: str,
        *,
        retry_seconds: float = 1,
    ) -> Generator[None, None, None]:
        yield
