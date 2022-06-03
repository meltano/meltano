"""Plugin requirements."""

from __future__ import annotations

from typing import TypeVar

from meltano.core.behavior import NameEq
from meltano.core.behavior.canonical import Canonical

TReq = TypeVar("TReq", bound="PluginRequirement")


class PluginRequirement(NameEq, Canonical):
    """A plugin requirement."""

    def __init__(self, name: str, variant: str | None = None) -> None:
        """Create a new PluginBundleFile.

        Args:
            name: The name of the plugin dependency.
            variant: The variant of the plugin dependency.
        """
        super().__init__(name=name, variant=variant)

    @classmethod
    def parse_all(cls: type[TReq], obj: dict | None) -> dict[str, list[TReq]]:
        """Deserialize requirements data into a dict of PluginRequirement.

        Args:
            obj: Raw Python object.

        Returns:
            Mapping of plugin types to requirements.
        """
        if obj is not None:
            return {
                plugin_type: [cls.parse(req) for req in requirements]
                for plugin_type, requirements in obj.items()
            }

        return {}
