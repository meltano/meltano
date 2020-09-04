import subprocess
import json
import logging
import asyncio
import os
import sys

from pathlib import Path
from datetime import datetime
from enum import IntFlag

from . import Runner, RunnerError
from meltano.core.job import Job, Payload, JobFinder
from meltano.core.plugin_invoker import invoker_factory, PluginInvoker
from meltano.core.plugin.singer import SingerTap, SingerTarget, PluginType
from meltano.core.utils import file_has_data, merge
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
        session,
        extractor_log=None,
        loader_log=None,
        extractor_out=None,
        loader_out=None,
    ):
        extractor_log = extractor_log or sys.stderr
        loader_log = loader_log or sys.stderr

        try:
            p_target, p_tap = None, None

            p_tap = await tap.invoke_async(
                stdout=asyncio.subprocess.PIPE,  # Singer messages
                stderr=asyncio.subprocess.PIPE,  # Log
            )

            p_target = await target.invoke_async(
                stdin=asyncio.subprocess.PIPE,  # Singer messages
                stdout=asyncio.subprocess.PIPE,  # Singer state
                stderr=asyncio.subprocess.PIPE,  # Log
            )
        except Exception as err:
            if p_tap:
                p_tap.kill()
            if p_target:
                p_target.kill()
            raise RunnerError(f"Cannot start tap or target: {err}") from err

        tap_outputs = [p_target.stdin]
        if extractor_out:
            tap_outputs.insert(0, extractor_out)

        target_outputs = [self.bookmark_writer(session)]
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
                f"Tap and target failed", {"extractor": tap_code, "loader": target_code}
            )
        elif tap_code:
            raise RunnerError(f"Tap failed", {"extractor": tap_code})
        elif target_code:
            raise RunnerError(f"Target failed", {"loader": target_code})

    def bookmark_writer(self, session):
        incomplete_state = self.context.full_refresh and self.context.select_filter
        payload_flag = Payload.INCOMPLETE_STATE if incomplete_state else Payload.STATE
        return BookmarkWriter(self.context.job, session, payload_flag=payload_flag)

    def restore_bookmark(self, session, tap: PluginInvoker):
        # Delete state left over from different pipeline run for same extractor
        try:
            os.remove(tap.files["state"])
        except OSError:
            pass

        if self.context.full_refresh:
            logging.info(
                "Performing full refresh, ignoring state left behind by any previous runs."
            )
            return

        if self.context.job is None:
            logging.info(
                f"Running outside a Job context: incremental state could not be loaded."
            )
            return

        # the `state.json` is stored in the database
        state = {}
        incomplete_since = None
        finder = JobFinder(self.context.job.job_id)

        state_job = finder.latest_with_payload(session, flags=Payload.STATE)
        if state_job:
            logging.info(f"Found state from {state_job.started_at}.")
            incomplete_since = state_job.ended_at
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        incomplete_state_jobs = finder.with_payload(
            session, flags=Payload.INCOMPLETE_STATE, since=incomplete_since
        )
        for state_job in incomplete_state_jobs:
            logging.info(f"Found incomplete state from {state_job.started_at}.")
            if "singer_state" in state_job.payload:
                merge(state_job.payload["singer_state"], state)

        if state:
            with tap.files["state"].open("w+") as state_file:
                json.dump(state, state_file, indent=2)
        else:
            logging.warning("No state was found, complete import.")

    def dry_run(self, tap: PluginInvoker, target: PluginInvoker):
        logging.info("Dry run:")
        logging.info(f"\textractor: {tap.plugin.name} at '{tap.exec_path()}'")
        logging.info(f"\tloader: {target.plugin.name} at '{target.exec_path()}'")

    async def run(
        self,
        session,
        extractor_log=None,
        loader_log=None,
        extractor_out=None,
        loader_out=None,
    ):
        tap = self.context.extractor_invoker()
        target = self.context.loader_invoker()

        if self.context.dry_run:
            return self.dry_run(tap, target)

        with tap.prepared(session), target.prepared(session):
            self.restore_bookmark(session, tap)

            await self.invoke(
                tap,
                target,
                session,
                extractor_log=extractor_log,
                loader_log=loader_log,
                extractor_out=extractor_out,
                loader_out=loader_out,
            )
