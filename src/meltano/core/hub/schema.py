"""Response schemas for the Meltano Hub API."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class IndexedPlugin:
    """Response schema for the plugin type index."""

    name: str
    default_variant: str
    variants: dict[str, VariantRef] = field(default_factory=dict)
    logo_url: str | None = None

    @property
    def variant_labels(self) -> list[str]:
        """Return a list of variant labels.

        Returns:
            A list of variant labels.
        """
        result = []
        variants = deepcopy(self.variants)
        default_variant = variants.pop(self.default_variant)
        result.append(f"{default_variant.name} (default)")

        for variant in variants.values():
            # Add here any other variant metadata like maintenance status, etc.
            result.append(variant.name)

        return result


@dataclass
class VariantRef:
    """Response schema for a plugin variant."""

    name: str
    ref: str
