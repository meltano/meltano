"""Bundled yaml files."""

from __future__ import annotations

import sys

if sys.version_info < (3, 9):
    import importlib_resources as resources
else:
    from importlib import resources

root = resources.files("meltano.core.bundle")
