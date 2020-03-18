import subprocess
import json
import logging
import asyncio
import os
import sys

from pathlib import Path
from datetime import datetime
from enum import IntFlag

from . import Runner
from meltano.core.job import Job, JobFinder
from meltano.core.plugin_invoker import invoker_factory, PluginInvoker
from meltano.core.config_service import ConfigService
from meltano.core.plugin.singer import SingerTap, SingerTarget, PluginType
from meltano.core.connection_service import ConnectionService
from meltano.core.utils import file_has_data
from meltano.core.logging import capture_subprocess_output
from meltano.core.elt_context import ELTContext


class SingerPayload(IntFlag):
    STATE = 1


class SingerRunner(Runner):
    def __init__(
        self,
        elt_context: ELTContext,
        config_service: ConfigService = None,
        connection_service: ConnectionService = None,
        **config,
    ):
        self.context = elt_context
        self.config = config
        self.config_service = config_service or ConfigService(elt_context.project)
        self.connection_service = connection_service or ConnectionService(elt_context)

        self.tap_config_dir = Path(config.get("tap_config_dir", "/etc/singer/tap"))
        self.target_config_dir = Path(
            config.get("target_config_dir", "/etc/singer/target")
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

    async def invoke(self, tap: PluginInvoker, target: PluginInvoker):
        try:
            # use standard pipes here because we
            # don't need async processing between the
            # tap and target.
            target_in, tap_out = os.pipe()

            p_target, p_tap = None, None
            p_target = await target.invoke_async(
                stdin=target_in,
                stdout=asyncio.subprocess.PIPE,  # state log
                stderr=asyncio.subprocess.PIPE,  # Target err for logging it
            )
            os.close(target_in)

            p_tap = await tap.invoke_async(
                stdout=tap_out, stderr=asyncio.subprocess.PIPE
            )
            os.close(tap_out)
        except Exception as err:
            if p_tap:
                p_tap.kill()
            if p_target:
                p_target.kill()
            raise Exception(f"Cannot start tap or target: {err}")

        # receive the target stdout and update the current job
        # for each line
        await asyncio.wait(
            [
                self.bookmark(p_target.stdout),
                capture_subprocess_output(p_tap.stderr, sys.stderr),
                capture_subprocess_output(p_target.stderr, sys.stderr),
                p_target.wait(),
                p_tap.wait(),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # at this point, something already stopped, the other component
        # should die soon because of a SIGPIPE
        target_code = await p_target.wait()
        tap_code = await p_tap.wait()

        if any((tap_code, target_code)):
            raise Exception(
                f"Subprocesses didn't exit cleanly: tap({tap_code}), target({target_code})"
            )

    def restore_bookmark(self, session, tap: PluginInvoker):
        if self.context.job is None:
            logging.info(
                f"Running outside a Job context: incremental state could not be loaded."
            )
            return

        # the `state.json` is stored in the database
        finder = JobFinder(self.context.job.job_id)
        state_job = finder.latest_with_payload(session, flags=SingerPayload.STATE)

        if state_job and "singer_state" in state_job.payload:
            logging.info(f"Found state from {state_job.started_at}.")
            with tap.files["state"].open("w+") as state:
                json.dump(state_job.payload["singer_state"], state)
        else:
            logging.warning("No state was found, complete import.")

            # Delete state left over from different pipeline run for same extractor
            try:
                os.remove(tap.files["state"])
            except OSError:
                pass

    def bookmark_state(self, new_state: str):
        if self.context.job is None:
            logging.info(
                f"Running outside a Job context: incremental state could not be updated."
            )
            return

        try:
            new_state = json.loads(new_state)
            job = self.context.job

            job.payload["singer_state"] = new_state
            job.payload_flags |= SingerPayload.STATE
            job.ended_at = datetime.utcnow()
            logging.info(f"Incremental state has been updated at {job.ended_at}.")
            logging.debug(f"Incremental state: {new_state}")
        except Exception as err:
            logging.warning(
                "Received state is invalid, incremental state has not been updated"
            )

    async def bookmark(self, target_stream):
        while not target_stream.at_eof():
            last_state = await target_stream.readline()
            if not last_state:
                continue

            self.bookmark_state(last_state)

    def dry_run(self, tap: PluginInvoker, target: PluginInvoker):
        logging.info("Dry run:")
        logging.info(f"\textractor: {tap.plugin.name} at '{tap.exec_path()}'")
        logging.info(f"\tloader: {target.plugin.name} at '{target.exec_path()}'")

    def run(self, session, dry_run=False):
        tap = self.context.extractor_invoker()
        target = self.context.loader_invoker()

        if dry_run:
            return self.dry_run(tap, target)

        # Sets the proper `schema` for the target from the ELTContext
        target_elt_params = self.connection_service.load_params()
        target.plugin_config.update(target_elt_params)

        tap.prepare(session)
        target.prepare(session)

        self.restore_bookmark(session, tap)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.invoke(tap, target))
