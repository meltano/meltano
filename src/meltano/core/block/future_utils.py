"""Various small utilities for working with futures."""

from __future__ import annotations

import asyncio
import logging
from asyncio import Task

from meltano.core.runner import RunnerError
from meltano.core.utils import human_size


def all_done(tasks: list[Task], done: set[Task]) -> bool:
    """Iterate through a task list checking if ALL tasks are in the done set."""
    return all(idx in done for idx in tasks)


def first_failed_future(exception_future: Task, done: set[Task]) -> Task | None:
    """Check if a future is completed and return the first failed (if any).

    Args:
        exception_future: The future you want to check and who's futures should
            be returned if an exception was raised.
        done: The set of completed futures you want to search.

    Returns:
        The first future that failed.
    """
    if exception_future in done:
        futures_done, _ = exception_future.result()
        futures_failed = [
            future for future in futures_done if future.exception() is not None
        ]

        if futures_failed:
            return futures_failed.pop()


def handle_producer_line_length_limit_error(
    exception: Exception,
    line_length_limit: int,
    stream_buffer_size: int,
):
    """Handle `asyncio.LimitOverrunError` from producers.

    Args:
        exception: The exception to handle, which should be a `ValueError` with
            a `asyncio.LimitOverrunError` as its context.
        line_length_limit: The message size limit.
        stream_buffer_size: The stream buffer size.

    Raises:
        RunnerError: An exception raised from the `asyncio.LimitOverrunError`.
    """
    # TODO: reuse from runner/singer.py
    # StreamReader.readline can raise a ValueError wrapping a LimitOverrunError:
    # https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L549
    if not isinstance(exception, ValueError):
        return

    exception = exception.__context__  # noqa: WPS609
    if not isinstance(exception, asyncio.LimitOverrunError):
        return

    logging.error(
        "The extractor generated a message exceeding the message size limit "
        f"of {human_size(line_length_limit)} (half the buffer size "
        f"of {human_size(stream_buffer_size)}).",
    )
    logging.error(
        "To let this message be processed, increase the 'elt.buffer_size' "
        "setting to at least double the size of the largest expected message, "
        "and try again.",
    )
    logging.error(
        "To learn more, visit "
        "https://docs.meltano.com/reference/settings#eltbuffer_size",
    )
    raise RunnerError("Output line length limit exceeded") from exception
