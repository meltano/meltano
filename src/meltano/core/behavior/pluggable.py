"""Make a feature pluggable with packaging plugins."""

from __future__ import annotations

import sys
import typing as t
from functools import cached_property

if sys.version_info >= (3, 12):
    from importlib.metadata import EntryPoints, entry_points
else:
    from importlib_metadata import EntryPoints, entry_points

T = t.TypeVar("T")


class Pluggable(t.Generic[T]):
    """Make a feature pluggable with packaging plugins."""

    def __init__(self, entry_point_group: str):
        """Create a new pluggable feature.

        Args:
            entry_point_group: The entry point group for the feature.
        """
        self.entry_point_group = entry_point_group

    @cached_property
    def meltano_plugins(self) -> EntryPoints:
        """List available plugins.

        Returns:
            List of available plugins.
        """
        return entry_points(group=self.entry_point_group)

    def get_all_meltano_plugins(self) -> dict[str, T]:
        """Get all plugins.

        Returns:
            All plugins.
        """
        return {ep.name: ep.load() for ep in self.meltano_plugins}

    def get_meltano_plugin(self, name: str) -> T:
        """Get a plugin by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugged object.
        """
        return self.meltano_plugins[name].load()
