"""File bundles required by plugins."""

from __future__ import annotations

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical


class PluginBundleFile(NameEq, Canonical):
    """A plugin bundle file."""

    def __init__(self, name: str, variant: str) -> None:
        """Create a new PluginBundleFile.

        Args:
            name: The name of the plugin bundle file.
            variant: The variant of the plugin bundle file.
        """
        super().__init__(name=name, variant=variant)


class PluginBundle(Canonical):
    """A plugin bundle."""

    def __init__(self, files: list | None = None) -> None:
        """Create a new PluginBundle.

        Args:
            files: The files of the plugin bundle.
        """
        super().__init__(files=list(map(PluginBundleFile.parse, files or [])))
