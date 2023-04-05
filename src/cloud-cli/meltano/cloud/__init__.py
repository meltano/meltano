"""Meltano Cloud."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata

try:
    __version__ = importlib_metadata.version("meltano-cloud-cli")
except importlib_metadata.PackageNotFoundError:
    __version__ = importlib_metadata.version("meltano")
