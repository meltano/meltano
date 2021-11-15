"""Various utils and formatters for log rendering control."""

from typing import Optional, Sequence

import structlog
from structlog.types import Processor

TIMESTAMPER = structlog.processors.TimeStamper(fmt="iso")

LEVELED_TIMESTAMPED_PRE_CHAIN = frozenset(
    (
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        TIMESTAMPER,
    )
)


def _process_formatter(processor: Processor):
    """Use _process_formatter to configure a structlog.stdlib.ProcessFormatter.

    It will automatically add log level and timestamp fields to any log entries not originating from structlog.

    Args:
        processor: A structlog message processor such as structlog.dev.ConsoleRenderer.
    """
    return structlog.stdlib.ProcessorFormatter(
        processor=processor, foreign_pre_chain=LEVELED_TIMESTAMPED_PRE_CHAIN
    )


def console_log_formatter(colors: bool = False) -> None:
    """Create a logging formatter for console rendering that supports colorization."""
    return _process_formatter(structlog.dev.ConsoleRenderer(colors=colors))


def key_value_formatter(
    sort_keys: bool = False,
    key_order: Optional[Sequence[str]] = None,
    drop_missing: bool = False,
) -> None:
    """Create a logging formatter that renders lines in key=value format."""
    return _process_formatter(
        processor=structlog.processors.KeyValueRenderer(
            sort_keys=sort_keys, key_order=key_order, drop_missing=drop_missing
        )
    )


def json_formatter() -> None:
    """Create a logging formatter that renders lines in JSON format."""
    return _process_formatter(processor=structlog.processors.JSONRenderer())
