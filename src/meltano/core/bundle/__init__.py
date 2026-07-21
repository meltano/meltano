"""Bundled yaml files."""

# ruff: file-ignore[non-empty-init-module]

from __future__ import annotations

import importlib.resources

root = importlib.resources.files("meltano.core.bundle")
