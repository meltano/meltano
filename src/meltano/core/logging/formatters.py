"""Various utils and formatters for log rendering control."""

from __future__ import annotations

import sys
import typing as t

import click
import structlog
import structlog.typing
from rich.console import Console
from rich.traceback import Traceback, install

from meltano.core.utils import get_boolean_env_var, get_no_color_flag

from .renderers import MeltanoConsoleRenderer

if sys.version_info >= (3, 11):
    from typing import Unpack  # noqa: ICN003
else:
    from typing_extensions import Unpack

if t.TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from types import TracebackType

    from structlog.types import Processor

install(suppress=[click])


def get_default_foreign_pre_chain() -> t.Sequence[Processor]:
    """Get the default foreign pre-chain for a ProcessorFormatter.

    This is the pre-chain that will be used for all ProcessorFormatter instances.
    """
    return (
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=not get_boolean_env_var("NO_UTC", default=False),
        ),
    )


class LoggingFeatures(t.TypedDict, total=False):
    """Logging features that can be enabled in a formatter."""

    callsite_parameters: bool
    """Enable filename, line number, and function name in log entries.

    https://www.structlog.org/en/stable/api.html#structlog.processors.CallsiteParameter.
    """

    dict_tracebacks: bool
    """Enable tracebacks dictionaries in log entries.

    https://www.structlog.org/en/stable/api.html#structlog.processors.dict_tracebacks.
    """

    show_locals: bool
    """Whether to show local variables in the traceback.

    https://www.structlog.org/en/stable/api.html#module-structlog.tracebacks.
    """


# Convert boolean kwargs to LoggingFeatures enum.
def _processors_from_kwargs(
    **features: Unpack[LoggingFeatures],
) -> t.Generator[Processor, None, None]:
    if features.get("callsite_parameters", False):
        yield structlog.processors.CallsiteParameterAdder(
            parameters=(
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
            ),
        )

    if features.get("dict_tracebacks", False):
        show_locals = features.get("show_locals", False)
        yield structlog.processors.ExceptionRenderer(
            structlog.tracebacks.ExceptionDictTransformer(show_locals=show_locals),
        )


def rich_exception_formatter_factory(
    color_system: t.Literal["auto", "standard", "256", "truecolor", "windows"] = "auto",
    *,
    no_color: bool | None = None,
    show_locals: bool = False,
    max_frames: int = 100,
) -> Callable[[t.TextIO, structlog.types.ExcInfo], None]:
    """Create an exception formatter for logging using the rich package.

    Examples:
    >>> rich_traceback = rich_exception_formatter_factory(color_system="truecolor")
    >>> plane_rich_traceback = rich_exception_formatter_factory(no_color=True)

    Args:
        color_system: The color system supported by your terminal.
        no_color: Enabled no color mode, or None to auto detect. Defaults to None.
        show_locals: Whether to show local variables in the traceback.
        max_frames: Maximum number of frames to show in a traceback, 0 for no maximum.

    Returns:
        Exception formatter function.
    """

    def _traceback(
        sio,  # noqa: ANN001
        exc_info: tuple[type[t.Any], BaseException, TracebackType | None],
    ) -> None:
        sio.write("\n")
        Console(file=sio, color_system=color_system, no_color=no_color).print(
            Traceback.from_exception(
                *exc_info,
                show_locals=show_locals,
                max_frames=max_frames,
            ),
        )

    return _traceback


def _process_formatter(
    *processors: Processor,
    **kwargs: t.Any,
) -> structlog.stdlib.ProcessorFormatter:
    """Use _process_formatter to configure a structlog.stdlib.ProcessFormatter.

    It will automatically add log level and timestamp fields to any log entries
    not originating from structlog.

    Args:
        *processors: One or more structlog message processors such as
            `structlog.dev.ConsoleRenderer`.
        **kwargs: Additional keyword arguments to pass to the logging.Formatter
            constructor.

    Returns:
        A log record formatter.
    """
    return structlog.stdlib.ProcessorFormatter(
        processors=processors,
        # FYI: this needs to be kept consistent between all `ProcessorFormatter`
        # instances
        foreign_pre_chain=get_default_foreign_pre_chain(),
        **kwargs,
    )


def console_log_formatter(
    *,
    colors: bool = False,
    callsite_parameters: bool = False,
    show_locals: bool = False,
    max_frames: int = 2,
    include_keys: Sequence[str] | None = None,
    all_keys: bool | None = None,
) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter for console rendering that supports colorization.

    Args:
        colors: Add color to output.
        callsite_parameters: Whether to include callsite parameters in the output.
        show_locals: Whether to show local variables in the traceback.
        max_frames: Maximum number of frames to show in a traceback, 0 for no maximum.
        include_keys: Include these keys in the output.
        all_keys: Whether to include all keys in the output.

    Returns:
        A configured console log formatter.
    """
    colors = colors and not get_no_color_flag()

    if colors:
        exception_formatter = rich_exception_formatter_factory(
            color_system="truecolor",
            show_locals=show_locals,
            max_frames=max_frames,
        )
    else:
        exception_formatter = rich_exception_formatter_factory(
            no_color=True,
            show_locals=show_locals,
            max_frames=max_frames,
        )

    return _process_formatter(
        *_processors_from_kwargs(callsite_parameters=callsite_parameters),
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        MeltanoConsoleRenderer(
            colors=colors,
            exception_formatter=exception_formatter,
            include_keys=set(include_keys) if include_keys else None,
            all_keys=all_keys,
        ),
    )


def key_value_formatter(
    *,
    sort_keys: bool = False,
    key_order: Sequence[str] | None = None,
    drop_missing: bool = False,
    callsite_parameters: bool = False,
) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter that renders lines in key=value format.

    Args:
        sort_keys: Whether to sort keys when formatting.
        key_order: List of keys that should be rendered in this exact order.
            Missing keys will be rendered as None, extra keys depending on
            *sort_keys* and the dict class.
        drop_missing: When True, extra keys in *key_order* will be dropped
            rather than rendered as None.
        callsite_parameters: Whether to include callsite parameters in the output.

    Returns:
        A configured key=value formatter.
    """
    return _process_formatter(
        *_processors_from_kwargs(callsite_parameters=callsite_parameters),
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.KeyValueRenderer(
            sort_keys=sort_keys,
            key_order=key_order,
            drop_missing=drop_missing,
        ),
    )


def json_formatter(
    *,
    callsite_parameters: bool = False,
    dict_tracebacks: bool = True,
    show_locals: bool = False,
) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter that renders lines in JSON format.

    Args:
        callsite_parameters: Whether to include callsite parameters in the JSON output.
        dict_tracebacks: Whether to include tracebacks in the JSON output.
        show_locals: Whether to include local variables in the traceback.

    Returns:
        A configured JSON formatter.
    """
    return _process_formatter(
        *_processors_from_kwargs(
            callsite_parameters=callsite_parameters,
            dict_tracebacks=dict_tracebacks,
            show_locals=show_locals,
        ),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.JSONRenderer(),
    )


def _event_renderer(
    logger: structlog.typing.WrappedLogger,  # noqa: ARG001
    name: str,  # noqa: ARG001
    event_dict: structlog.typing.EventDict,
) -> str | bytes:
    """Render an event dictionary as a string.

    Args:
        logger: The logger instance.
        name: The logger name.
        event_dict: The event dictionary.

    Returns:
        The rendered event dictionary.
    """
    return event_dict["event"]


def plain_formatter(
    *,
    fmt: str | None = None,
    datefmt: str | None = None,
    style: str = "%",
    validate: bool = True,
) -> structlog.stdlib.ProcessorFormatter:
    """Create a logging formatter that renders lines in a simple format.

    Args:
        fmt: The format string.
        datefmt: The date format string.
        style: The format style.
        validate: Whether to validate the format string.
        features: Logging features to enable.

    Returns:
        A configured simple formatter.
    """
    return _process_formatter(
        structlog.stdlib.ExtraAdder(),
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _event_renderer,
        fmt=fmt,
        datefmt=datefmt,
        style=style,
        validate=validate,
    )
