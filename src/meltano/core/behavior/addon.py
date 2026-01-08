"""Meltano add-ons installable as packaging plugins."""

from __future__ import annotations

import sys
import typing as t
from functools import cached_property

if sys.version_info >= (3, 12):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

if t.TYPE_CHECKING:
    if sys.version_info >= (3, 12):
        from importlib.metadata import EntryPoints
    else:
        from importlib_metadata import EntryPoints

T = t.TypeVar("T")

# Module-level cache to avoid repeated package scans across all MeltanoAddon instances
_ENTRY_POINTS_CACHE: dict[str, EntryPoints] = {}


class MeltanoAddon(t.Generic[T]):
    """A Meltano add-on with packaging plugins."""

    def __init__(self, entry_point_group: str):
        """Create a new Meltano add-on.

        Args:
            entry_point_group: The entry point group for the feature.
        """
        self.entry_point_group = entry_point_group

    @cached_property
    def installed(self) -> EntryPoints:
        """List installed add-ons with module-level caching.

        Returns:
            List of available add-ons.
        """
        if self.entry_point_group not in _ENTRY_POINTS_CACHE:
            _ENTRY_POINTS_CACHE[self.entry_point_group] = entry_points(
                group=self.entry_point_group,
            )
        return _ENTRY_POINTS_CACHE[self.entry_point_group]

    def get_all(self) -> t.Generator[T, None, None]:
        """Get all add-ons.

        Returns:
            All add-ons.
        """
        for ep in self.installed:
            yield ep.load()

    def get(self, name: str) -> T:
        """Get an add-on by name.

        Args:
            name: The name of the add-on.

        Returns:
            The add-on object.
        """
        return self.installed[name].load()
