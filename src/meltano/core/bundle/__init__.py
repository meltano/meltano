"""Bundled yaml files."""

from __future__ import annotations

from meltano.core.utils.compat import importlib_resources

root = importlib_resources.files(__package__)
