"""Compatibility layer for different Python versions."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 12):
    from typing import override  # noqa: ICN003
else:
    from typing_extensions import override

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

__all__ = [
    "deprecated",
    "override",
]


class MeltanoInternalDeprecationWarning(DeprecationWarning):
    """Warning for deprecated internal Meltano APIs."""
