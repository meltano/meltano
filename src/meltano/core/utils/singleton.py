"""Provides a metaclass that creates singletons."""

from __future__ import annotations

from abc import ABCMeta
from typing import Any


class SingletonMeta(ABCMeta):
    """A metaclass that creates singletons."""

    def __init__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]):
        """Initialize the metaclass.

        Parameters:
            name: The name of the new class to create.
            bases: The base classes of the new class.
            namespace: The dict of the new class.
        """
        super().__init__(name, bases, namespace)
        cls._singleton_instance = None

    def __call__(cls) -> Any:
        """Create the single instance of the class if needed, and return it.

        Returns:
            The single instance of the class.
        """
        if cls._singleton_instance is None:
            cls._singleton_instance = super().__call__()
        return cls._singleton_instance
