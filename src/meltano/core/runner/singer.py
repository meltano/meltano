from __future__ import annotations  # noqa: D100

import asyncio
import subprocess
import sys
import typing as t

import structlog

from meltano.core.logging import capture_subprocess_output
from meltano.core.plugin import PluginType
from meltano.core.runner import Runner, RunnerError
from meltano.core.utils import human_size

if t.TYPE_CHECKING:
    from meltano.core.elt_context import ELTContext
    from meltano.core.plugin_invoker import PluginInvoker


logger = structlog.stdlib.get_logger(__name__)


class SingerRunner(Runner):  # noqa: D101
    def __init__(self, elt_context: ELTContext):  # noqa: D107
        self.context = elt_context

    def stop(self, process, **wait_args):  # noqa: ANN001, ANN003, ANN201, D102
        while True:  # pragma: no cover
            try:
                code = process.wait(**wait_args)
                logger.debug(f"{process} exited with {code}")  # noqa: G004
                return code
            except subprocess.TimeoutExpired:  # noqa: PERF203
                process.kill()
                logger.error(f"{process} was killed.")  # noqa: G004

    async def invoke(
        self,
        tap: PluginInvoker,
        target: PluginInvoker,
        extractor_log=None,  # noqa: ANN001
        loader_log=None,  # noqa: ANN001
        extractor_out=None,  # noqa: ANN001
        loader_out=None,  # noqa: ANN001
    ) -> None:
        """Invoke tap and target together."""
        extractor_log = extractor_log or sys.stderr
        loader_log = loader_log or sys.stderr

        # The StreamReader line length limit also acts as half the buffer size,
        # which cannot be set directly:
        # https://github.com/python/cpython/blob/v3.12.7/Lib/asyncio/streams.py#L423-L424
        # https://github.com/python/cpython/blob/v3.12.7/Lib/asyncio/streams.py#L510
        stream_buffer_size = self.context.project.settings.get("elt.buffer_size")
        line_length_limit = stream_buffer_size // 2

        # Start tap
        try:
            p_tap = await tap.invoke_async(
                limit=line_length_limit,
                stdout=asyncio.subprocess.PIPE,  # Singer messages
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start extractor: {err}") from err  # noqa: EM102

        # Start target
        try:
            p_target = await target.invoke_async(
                limit=line_length_limit,
                stdin=asyncio.subprocess.PIPE,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start loader: {err}") from err  # noqa: EM102

        # Process tap output
        tap_outputs = [p_target.stdin]
        if extractor_out:
            tap_outputs.insert(0, extractor_out)

        tap_stdout_future = asyncio.ensure_future(
            # forward subproc stdout to tap_outputs (i.e. targets stdin)
            capture_subprocess_output(p_tap.stdout, *tap_outputs),
        )
        tap_stderr_future = asyncio.ensure_future(
            capture_subprocess_output(p_tap.stderr, extractor_log),
        )

        # Process target output
        target_outputs = []
        if target.output_handlers:
            target_outputs = target.output_handlers.get(target.StdioSource.STDOUT, [])

        if loader_out:
            target_outputs.insert(0, loader_out)

        target_stdout_future = asyncio.ensure_future(
            capture_subprocess_output(p_target.stdout, *target_outputs),
        )
        target_stderr_future = asyncio.ensure_future(
            capture_subprocess_output(p_target.stderr, loader_log),
        )

        # Wait for tap or target to complete, or for one of the output handlers
        # to raise an exception.
        tap_process_future = asyncio.ensure_future(p_tap.wait())
        target_process_future = asyncio.ensure_future(p_target.wait())
        output_exception_future = asyncio.ensure_future(
            asyncio.wait(
                [
                    tap_stdout_future,
                    tap_stderr_future,
                    target_stdout_future,
                    target_stderr_future,
                ],
                return_when=asyncio.FIRST_EXCEPTION,
            ),
        )

        done, _ = await asyncio.wait(
            [tap_process_future, target_process_future, output_exception_future],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # If `output_exception_future` completes first, one of the output
        # handlers raised an exception or all completed successfully.
        if output_exception_future in done:
            output_futures_done, _ = output_exception_future.result()
            if output_futures_failed := [
                future
                for future in output_futures_done
                if future.exception() is not None
            ]:
                # If any output handler raised an exception, re-raise it.

                # Special behavior for the tap stdout handler raising a line
                # length limit error.
                if tap_stdout_future in output_futures_failed:
                    self._handle_tap_line_length_limit_error(
                        tap_stdout_future.exception(),
                        line_length_limit=line_length_limit,
                        stream_buffer_size=stream_buffer_size,
                    )

                failed_future = output_futures_failed.pop()
                raise failed_future.exception()

            # If all of the output handlers completed without raising an
            # exception, we still need to wait for the tap or target to
            # complete.
            done, _ = await asyncio.wait(
                [tap_process_future, target_process_future],
                return_when=asyncio.FIRST_COMPLETED,
            )

        if target_process_future in done:
            target_code = target_process_future.result()

            if tap_process_future in done:
                tap_code = tap_process_future.result()
            else:
                # If the target completes before the tap, it failed before
                # processing all tap output

                # Kill tap and cancel output processing since there's no more
                # target to forward messages to
                p_tap.kill()
                await tap_process_future
                tap_stdout_future.cancel()
                tap_stderr_future.cancel()

                # Pretend the tap finished successfully since it didn't itself fail
                tap_code = 0

            # Wait for all buffered target output to be processed
            await asyncio.wait([target_stdout_future, target_stderr_future])
        else:  # if tap_process_future in done:
            # If the tap completes before the target, the target should have a
            # chance to process all tap output
            tap_code = tap_process_future.result()

            # Wait for all buffered tap output to be processed
            await asyncio.wait([tap_stdout_future, tap_stderr_future])

            # Close target stdin so process can complete naturally
            p_target.stdin.close()
            await p_target.stdin.wait_closed()

            # Wait for all buffered target output to be processed
            await asyncio.wait([target_stdout_future, target_stderr_future])

            # Wait for target to complete
            target_code = await target_process_future

        if tap_code and target_code:
            raise RunnerError(
                "Extractor and loader failed",  # noqa: EM101
                {PluginType.EXTRACTORS: tap_code, PluginType.LOADERS: target_code},
            )
        if tap_code:
            raise RunnerError("Extractor failed", {PluginType.EXTRACTORS: tap_code})  # noqa: EM101
        if target_code:
            raise RunnerError("Loader failed", {PluginType.LOADERS: target_code})  # noqa: EM101

    def dry_run(self, tap: PluginInvoker, target: PluginInvoker) -> None:  # noqa: D102
        logger.info("Dry run:")
        logger.info(f"\textractor: {tap.plugin.name} at '{tap.exec_path()}'")  # noqa: G004
        logger.info(f"\tloader: {target.plugin.name} at '{target.exec_path()}'")  # noqa: G004

    async def run(  # noqa: ANN201, D102
        self,
        extractor_log=None,  # noqa: ANN001
        loader_log=None,  # noqa: ANN001
        extractor_out=None,  # noqa: ANN001
        loader_out=None,  # noqa: ANN001
    ):
        tap = self.context.extractor_invoker()
        target = self.context.loader_invoker()

        if self.context.dry_run:
            return self.dry_run(tap, target)

        async with (
            tap.prepared(self.context.session),
            target.prepared(self.context.session),
        ):
            await self.invoke(  # noqa: RET503
                tap,
                target,
                extractor_log=extractor_log,
                loader_log=loader_log,
                extractor_out=extractor_out,
                loader_out=loader_out,
            )

    def _handle_tap_line_length_limit_error(
        self,
        exception,  # noqa: ANN001
        line_length_limit,  # noqa: ANN001
        stream_buffer_size,  # noqa: ANN001
    ) -> None:
        # StreamReader.readline can raise a ValueError wrapping a LimitOverrunError:
        # https://github.com/python/cpython/blob/v3.12.7/Lib/asyncio/streams.py#L577
        if not isinstance(exception, ValueError):
            return

        exception = exception.__context__
        if not isinstance(exception, asyncio.LimitOverrunError):  # pragma: no cover
            return

        logger.error(
            f"The extractor generated a message exceeding the message size "  # noqa: G004
            f"limit of {human_size(line_length_limit)} (half the buffer size "
            f"of {human_size(stream_buffer_size)}).",
        )
        logger.error(
            "To let this message be processed, increase the 'elt.buffer_size' "
            "setting to at least double the size of the largest expected "
            "message, and try again.",
        )
        logger.error(
            "To learn more, visit "
            "https://docs.meltano.com/reference/settings#eltbuffer_size",
        )
        raise RunnerError("Output line length limit exceeded") from exception  # noqa: EM101
