"""Mixin for objects that have a name attribute and can be compared by name."""

from __future__ import annotations

import sys
import typing as t

if sys.version_info >= (3, 11):
    from typing import Self  # noqa: ICN003
else:
    from typing_extensions import Self

if t.TYPE_CHECKING:
    from collections.abc import Iterable


class NameEq:
    """Mixin for objects that have a name attribute and can be compared by name."""

    name: str

    def __eq__(self, value: object, /) -> bool:
        """Compare two NameEq objects for equality."""
        return isinstance(value, NameEq) and (self is value or self.name == value.name)

    def __hash__(self) -> int:
        """Return the hash of the named object."""
        return hash(self.name)

    @classmethod
    def find_by_name(cls, xs: Iterable[Self], name: str) -> Self | None:
        """Find a NameEq object by its name."""
        return next((x for x in xs if x.name == name), None)
