"""Various utils and formatters for log rendering control."""

from __future__ import annotations

from typing import Sequence, TextIO

import click
import structlog
from rich.console import Console
from rich.traceback import Traceback, install
from structlog.types import Processor

install(suppress=[click])

TIMESTAMPER = structlog.processors.TimeStamper(fmt="iso")

LEVELED_TIMESTAMPED_PRE_CHAIN = frozenset(
    (
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        TIMESTAMPER,
    )
)


def plain_rich_traceback(sio: TextIO, exc_info: structlog.types.ExcInfo) -> None:
    """Pretty-print `exc_info` to `sio` using the rich package, with colors disabled.

    To be passed into `ConsoleRenderer`'s `exception_formatter` argument.

    Args:
        sio: Return of open() in text mode.
        exc_info: Execution info.
    """
    sio.write("\n")
    Console(file=sio, no_color=True).print(
        Traceback.from_exception(*exc_info, show_locals=True)
    )


def _process_formatter(processor: Processor) -> structlog.stdlib.ProcessorFormatter:
    """Use _process_formatter to configure a structlog.stdlib.ProcessFormatter.

    It will automatically add log level and timestamp fields to any log entries not originating from structlog.

    Args:
        processor: A structlog message processor such as structlog.dev.ConsoleRenderer.

    Returns:
        A configured log processor.
    """
    return structlog.stdlib.ProcessorFormatter(
        processor=processor, foreign_pre_chain=LEVELED_TIMESTAMPED_PRE_CHAIN
    )


def console_log_formatter(colors: bool = False) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter for console rendering that supports colorization.

    Args:
        colors: Add color to output.

    Returns:
        A configured console log formatter.
    """
    exception_formatter = (
        structlog.dev.rich_traceback if colors else plain_rich_traceback
    )
    return _process_formatter(
        structlog.dev.ConsoleRenderer(
            colors=colors, exception_formatter=exception_formatter
        )
    )


def key_value_formatter(
    sort_keys: bool = False,
    key_order: Sequence[str] | None = None,
    drop_missing: bool = False,
) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter that renders lines in key=value format.

    Args:
        sort_keys: Whether to sort keys when formatting.
        key_order: List of keys that should be rendered in this exact order. Missing keys will be rendered as None, extra keys depending on *sort_keys* and the dict class.
        drop_missing: When True, extra keys in *key_order* will be dropped rather than rendered as None.

    Returns:
        A configured key=value formatter.
    """
    return _process_formatter(
        processor=structlog.processors.KeyValueRenderer(
            sort_keys=sort_keys, key_order=key_order, drop_missing=drop_missing
        )
    )


def json_formatter() -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter that renders lines in JSON format.

    Returns:
        A configured JSON formatter.
    """
    return _process_formatter(processor=structlog.processors.JSONRenderer())
