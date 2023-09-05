"""Meltano."""

from __future__ import annotations

from importlib import metadata

__version__ = metadata.version(__package__)

del annotations, metadata
