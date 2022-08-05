"""Exception context for the Snowplow tracker."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from types import TracebackType
from typing import Dict, List, Union

from snowplow_tracker import SelfDescribingJson

from meltano.core.tracking.schemas import ExceptionContextSchema
from meltano.core.utils import hash_sha256

BASE_PATHS = (sys.prefix, sys.exec_prefix, sys.base_prefix, sys.base_exec_prefix)

TracebackLevelsJSON = List[Dict[str, Union[str, int]]]
ExceptionContextJSON = Dict[
    str, Union[str, TracebackLevelsJSON, "ExceptionContextJSON"]
]


class ExceptionContext(SelfDescribingJson):
    """Exception context for the Snowplow tracker."""

    def __init__(self):
        """Initialize the exceptions context with the exceptions currently being handled."""
        ex = sys.exc_info()[1]
        super().__init__(
            ExceptionContextSchema.url,
            {
                "context_uuid": str(uuid.uuid4()),
                "exception": None if ex is None else get_exception_json(ex),
            },
        )


def get_exception_json(ex: BaseException) -> ExceptionContextJSON:
    """Get anonymized telemetry data detailing an exception.

    Args:
        ex: The exception from which data will be extracted.

    Returns:
        A JSON-compatible dictionary of anonymized telemetry data compliant with the exception
        context schema for an exception.
    """
    cause, context, tb = ex.__cause__, ex.__context__, ex.__traceback__  # noqa: WPS609
    return {
        "type": str(type(ex).__qualname__),
        "str_hash": hash_sha256(str(ex)),
        "repr_hash": hash_sha256(repr(ex)),
        "traceback": None if tb is None else get_traceback_json(tb),
        "cause": None if cause is None else get_exception_json(cause),
        "context": None if context is None else get_exception_json(context),
    }


def get_traceback_json(tb: TracebackType) -> TracebackLevelsJSON:
    """Get anonymized telemetry data detailing a traceback.

    Args:
        tb: The traceback from which data will be extracted.

    Returns:
        A list where each successive element details a lower level in the traceback.
    """
    levels = []
    while tb:
        levels.append(
            {
                "file": get_relative_traceback_path(tb),
                "line_number": tb.tb_lineno,
            }
        )
        tb = tb.tb_next
    return levels


def get_relative_traceback_path(tb: TracebackType) -> str | None:
    """Get an anonymous path from a traceback by making it relative if possible.

    The path is made relative to the first element in `BASE_PATHS` it can be made relative to.

    Args:
        tb: The traceback from which to extract the path info.

    Returns:
        The first valid option of the following is returned:
        - If the path is `'<stdin>'`: `'<stdin>'`
        - If possible: the path made relative to a path in `BASE_PATHS`
        - If the file name is `__init__.py` or `__main__.py`: `'.../<module name>/<file name>.py'`.
        - Otherwise: `'.../<filename>.py'`.
    """
    try:
        str_path = tb.tb_frame.f_code.co_filename
    except Exception:
        return None

    if str_path == "<stdin>":
        return str_path

    path = Path(str_path)

    for base_path in BASE_PATHS:
        try:
            return path.relative_to(base_path).as_posix()
        except ValueError:  # Path could not be made relative to `base_path`
            pass  # Try making it relative to the next base path

    if path.parts[-1] in {"__init__.py", "__main__.py"}:
        # Include the module directory if the file is `__init__.py` or `__main__.py`
        return f".../{path.parts[-2]}/{path.parts[-1]}"
    return f".../{path.parts[-1]}"
