"""Meltano Cloud."""

from __future__ import annotations

from importlib import metadata as importlib_metadata

try:
    __version__ = importlib_metadata.version("meltano-cloud-cli")
except importlib_metadata.PackageNotFoundError:
    __version__ = importlib_metadata.version("meltano")
