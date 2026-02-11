"""Compatibility layer for different Python versions."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

__all__ = [
    "deprecated",
]


class MeltanoInternalDeprecationWarning(DeprecationWarning):
    """Warning for deprecated internal Meltano APIs."""
