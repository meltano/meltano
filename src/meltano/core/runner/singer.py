import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from contextlib import suppress
from datetime import datetime
from enum import IntFlag
from pathlib import Path

from meltano.core.elt_context import ELTContext
from meltano.core.job import Job, Payload
from meltano.core.logging import capture_subprocess_output
from meltano.core.plugin import PluginType
from meltano.core.plugin.singer import PluginType, SingerTap, SingerTarget
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils import human_size

from . import Runner, RunnerError


class BookmarkWriter:
    def __init__(self, job, session, payload_flag=Payload.STATE):
        self.job = job
        self.session = session
        self.payload_flag = payload_flag

    def writeline(self, line):
        if self.job is None:
            logging.info(
                f"Running outside a Job context: incremental state could not be updated."
            )
            return

        try:
            new_state = json.loads(line)
            job = self.job

            job.payload["singer_state"] = new_state
            job.payload_flags |= self.payload_flag
            job.save(self.session)

            logging.info(f"Incremental state has been updated at {datetime.utcnow()}.")
            logging.debug(f"Incremental state: {new_state}")
        except Exception as err:
            logging.warning(
                "Received state is invalid, incremental state has not been updated"
            )


class SingerRunner(Runner):
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

        self.project_settings_service = ProjectSettingsService(
            self.context.project,
            config_service=self.context.plugins_service.config_service,
        )

    def stop(self, process, **wait_args):
        while True:
            try:
                code = process.wait(**wait_args)
                logging.debug(f"{process} exited with {code}")
                return code
            except subprocess.TimeoutExpired:
                process.kill()
                logging.error(f"{process} was killed.")

    async def invoke(  # noqa: WPS217, WPS210, WPS213, WPS231
        self,
        tap: PluginInvoker,
        target: PluginInvoker,
        extractor_log=None,
        loader_log=None,
        extractor_out=None,
        loader_out=None,
    ):
        """Invoke tap and target together."""
        extractor_log = extractor_log or sys.stderr
        loader_log = loader_log or sys.stderr

        # The StreamReader line length limit also acts as half the buffer size,
        # which cannot be set directly:
        # - https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L395-L396
        # - https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L482
        stream_buffer_size = self.project_settings_service.get("elt.buffer_size")
        line_length_limit = stream_buffer_size // 2

        # Start tap
        try:
            p_tap = await tap.invoke_async(
                limit=line_length_limit,
                stdout=asyncio.subprocess.PIPE,  # Singer messages
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start extractor: {err}") from err

        # Start target
        try:
            p_target = await target.invoke_async(
                limit=line_length_limit,
                stdin=asyncio.subprocess.PIPE,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start loader: {err}") from err

        # Process tap output
        tap_outputs = [p_target.stdin]
        if extractor_out:
            tap_outputs.insert(0, extractor_out)

        tap_stdout_future = asyncio.ensure_future(
            capture_subprocess_output(p_tap.stdout, *tap_outputs)
        )
        tap_stderr_future = asyncio.ensure_future(
            capture_subprocess_output(p_tap.stderr, extractor_log)
        )

        # Process target output
        target_outputs = [self.bookmark_writer()]
        if loader_out:
            target_outputs.insert(0, loader_out)

        target_stdout_future = asyncio.ensure_future(
            capture_subprocess_output(p_target.stdout, *target_outputs)
        )
        target_stderr_future = asyncio.ensure_future(
            capture_subprocess_output(p_target.stderr, loader_log)
        )

        # Wait for tap or target to complete, or for one of the output handlers to raise an exception.
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

        # If `output_exception_future` completes first, one of the output handlers raised an exception or all completed successfully.
        if output_exception_future in done:
            output_futures_done, _ = output_exception_future.result()
            output_futures_failed = [
                future
                for future in output_futures_done
                if future.exception() is not None
            ]

            if output_futures_failed:
                # If any output handler raised an exception, re-raise it.

                # Special behavior for the tap stdout handler raising a line length limit error.
                if tap_stdout_future in output_futures_failed:
                    self._handle_tap_line_length_limit_error(
                        tap_stdout_future.exception(),
                        line_length_limit=line_length_limit,
                        stream_buffer_size=stream_buffer_size,
                    )

                failed_future = output_futures_failed.pop()
                raise failed_future.exception()
            else:
                # If all of the output handlers completed without raising an exception,
                # we still need to wait for the tap or target to complete.
                done, _ = await asyncio.wait(
                    [tap_process_future, target_process_future],
                    return_when=asyncio.FIRST_COMPLETED,
                )

        if target_process_future in done:
            target_code = target_process_future.result()

            if tap_process_future in done:
                tap_code = tap_process_future.result()
            else:
                # If the target completes before the tap, it failed before processing all tap output

                # Kill tap and cancel output processing since there's no more target to forward messages to
                p_tap.kill()
                await tap_process_future
                tap_stdout_future.cancel()
                tap_stderr_future.cancel()

                # Pretend the tap finished successfully since it didn't itself fail
                tap_code = 0

            # Wait for all buffered target output to be processed
            await asyncio.wait([target_stdout_future, target_stderr_future])
        else:  # if tap_process_future in done:
            # If the tap completes before the target, the target should have a chance to process all tap output
            tap_code = tap_process_future.result()

            # Wait for all buffered tap output to be processed
            await asyncio.wait([tap_stdout_future, tap_stderr_future])

            # Close target stdin so process can complete naturally
            p_target.stdin.close()
            with suppress(AttributeError):  # `wait_closed` is Python 3.7+
                await p_target.stdin.wait_closed()

            # Wait for all buffered target output to be processed
            await asyncio.wait([target_stdout_future, target_stderr_future])

            # Wait for target to complete
            target_code = await target_process_future

        if tap_code and target_code:
            raise RunnerError(
                "Extractor and loader failed",
                {PluginType.EXTRACTORS: tap_code, PluginType.LOADERS: target_code},
            )
        elif tap_code:
            raise RunnerError("Extractor failed", {PluginType.EXTRACTORS: tap_code})
        elif target_code:
            raise RunnerError("Loader failed", {PluginType.LOADERS: target_code})

    def bookmark_writer(self):
        incomplete_state = self.context.full_refresh and self.context.select_filter
        payload_flag = Payload.INCOMPLETE_STATE if incomplete_state else Payload.STATE
        return BookmarkWriter(
            self.context.job, self.context.session, payload_flag=payload_flag
        )

    def dry_run(self, tap: PluginInvoker, target: PluginInvoker):
        logging.info("Dry run:")
        logging.info(f"\textractor: {tap.plugin.name} at '{tap.exec_path()}'")
        logging.info(f"\tloader: {target.plugin.name} at '{target.exec_path()}'")

    async def run(
        self, extractor_log=None, loader_log=None, extractor_out=None, loader_out=None
    ):
        tap = self.context.extractor_invoker()
        target = self.context.loader_invoker()

        if self.context.dry_run:
            return self.dry_run(tap, target)

        with tap.prepared(self.context.session), target.prepared(self.context.session):
            await self.invoke(
                tap,
                target,
                extractor_log=extractor_log,
                loader_log=loader_log,
                extractor_out=extractor_out,
                loader_out=loader_out,
            )

    def _handle_tap_line_length_limit_error(
        self,
        exception,
        line_length_limit,
        stream_buffer_size,
    ):
        # StreamReader.readline can raise a ValueError wrapping a LimitOverrunError:
        # https://github.com/python/cpython/blob/v3.8.7/Lib/asyncio/streams.py#L549
        if not isinstance(exception, ValueError):
            return

        exception = exception.__context__  # noqa: WPS609
        if not isinstance(exception, asyncio.LimitOverrunError):
            return

        logging.error(
            f"The extractor generated a message exceeding the message size limit of {human_size(line_length_limit)} (half the buffer size of {human_size(stream_buffer_size)})."
        )
        logging.error(
            "To let this message be processed, increase the 'elt.buffer_size' setting to at least double the size of the largest expected message, and try again."
        )
        logging.error(
            "To learn more, visit https://www.meltano.com/docs/settings.html#elt-buffer-size"
        )
        raise RunnerError("Output line length limit exceeded") from exception
