"""Base context helpers for the Snowplow tracker."""

from __future__ import annotations

import typing as t

from meltano.core.utils import uuid7

if t.TYPE_CHECKING:
    import uuid


def new_context_uuid() -> uuid.UUID:
    """Generate a new context UUID.

    Returns:
        A new context UUID.
    """
    return uuid7()
