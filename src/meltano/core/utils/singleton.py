from __future__ import annotations

from abc import ABCMeta
from typing import Any


class SingletonMeta(ABCMeta):
    def __init__(self, name: str, bases: tuple[type], namespace: dict[str, Any]):
        super().__init__(name, bases, namespace)
        self._singleton_instance = None

    def __call__(self):
        if self._singleton_instance is None:
            self._singleton_instance = super().__call__()
        return self._singleton_instance
