"""Constants used by Meltano."""

from __future__ import annotations

import logging

CRON_INTERVALS: dict[str, str | None] = {
    "@once": None,
    "@manual": None,
    "@none": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}

LEVELS: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

SINGER_STATE_KEY = "singer_state"

STATE_ID_COMPONENT_DELIMITER = ":"
