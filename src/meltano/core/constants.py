"""Constants used by Meltano."""

from __future__ import annotations

import sys

if sys.version_info < (3, 15):
    from typing_extensions import sentinel  # type: ignore[attr-defined]


STATE_ID_COMPONENT_DELIMITER = ":"

LOG_PARSER_SINGER_SDK = "singer-sdk"

UNSET = sentinel("UNSET")
"""Marks a value as absent from a given store.

Distinct from an explicit `None`, which means the store *does* have the
setting, and its value has intentionally been set to `null`.
"""
