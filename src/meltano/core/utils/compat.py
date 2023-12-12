"""Compatibility utilities."""

from __future__ import annotations

import sys

if sys.version_info < (3, 9):
    import importlib_resources
else:
    from importlib import resources as importlib_resources

__all__ = ["importlib_resources"]
