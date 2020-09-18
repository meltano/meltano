import subprocess
import json
import logging
import asyncio
import os
import sys
import shutil

from pathlib import Path
from datetime import datetime
from enum import IntFlag

from . import Runner, RunnerError
from meltano.core.job import Job, Payload
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import invoker_factory, PluginInvoker
from meltano.core.plugin.singer import SingerTap, SingerTarget, PluginType
from meltano.core.utils import file_has_data
from meltano.core.logging import capture_subprocess_output
from meltano.core.elt_context import ELTContext


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

    def flush(self):
        pass


class SingerRunner(Runner):
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    def stop(self, process, **wait_args):
        while True:
            try:
                code = process.wait(**wait_args)
                logging.debug(f"{process} exited with {code}")
                return code
            except subprocess.TimeoutExpired:
                process.kill()
                logging.error(f"{process} was killed.")

    async def invoke(
        self,
        tap: PluginInvoker,
        target: PluginInvoker,
        extractor_log=None,
        loader_log=None,
        extractor_out=None,
        loader_out=None,
    ):
        extractor_log = extractor_log or sys.stderr
        loader_log = loader_log or sys.stderr

        try:
            p_tap = await tap.invoke_async(
                stdout=asyncio.subprocess.PIPE,  # Singer messages
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start tap: {err}") from err

        try:
            p_target = await target.invoke_async(
                stdin=asyncio.subprocess.PIPE,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            raise RunnerError(f"Cannot start target: {err}") from err

        tap_outputs = [p_target.stdin]
        if extractor_out:
            tap_outputs.insert(0, extractor_out)

        target_outputs = [self.bookmark_writer()]
        if loader_out:
            target_outputs.insert(0, loader_out)

        await asyncio.wait(
            [
                capture_subprocess_output(p_tap.stdout, *tap_outputs),
                capture_subprocess_output(p_tap.stderr, extractor_log),
                p_tap.wait(),
                capture_subprocess_output(p_target.stdout, *target_outputs),
                capture_subprocess_output(p_target.stderr, loader_log),
                p_target.wait(),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Close both sides of the tap-target pipe, so that both quit if they haven't already.
        p_tap.stdout._transport.close()
        p_target.stdin.close()

        # at this point, something already stopped, the other component
        # should die soon because of a SIGPIPE
        tap_code = await p_tap.wait()
        target_code = await p_target.wait()

        if tap_code and target_code:
            raise RunnerError(
                f"Tap and target failed",
                {PluginType.EXTRACTORS: tap_code, PluginType.LOADERS: target_code},
            )
        elif tap_code:
            raise RunnerError(f"Tap failed", {PluginType.EXTRACTORS: tap_code})
        elif target_code:
            raise RunnerError(f"Target failed", {PluginType.LOADERS: target_code})

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
