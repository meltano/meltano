import subprocess
import json
import logging
import asyncio
import os
from pathlib import Path
from datetime import datetime
from enum import IntFlag

from . import Runner
from meltano.core.db import project_engine
from meltano.core.job import Job, JobFinder
from meltano.core.project import Project
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.config_service import ConfigService
from meltano.core.plugin.singer import SingerTap, SingerTarget, PluginType
from meltano.core.utils import file_has_data


class SingerPayload(IntFlag):
    STATE = 1


class SingerRunner(Runner):
    def __init__(
        self, project: Project, job_id, config_service: ConfigService = None, **config
    ):
        self.project = project
        self.job_id = job_id
        self.config_service = config_service or ConfigService(project)
        self.config = config

        self.job = Job(job_id=self.job_id)
        self.run_dir = Path(config.get("run_dir", "/run/singer"))
        self.tap_config_dir = Path(config.get("tap_config_dir", "/etc/singer/tap"))
        self.target_config_dir = Path(
            config.get("target_config_dir", "/etc/singer/target")
        )

        _, self._session_cls = project_engine(project)

    @property
    def database(self):
        return self.config.get("database", "default")

    def stop(self, process, **wait_args):
        while True:
            try:
                code = process.wait(**wait_args)
                logging.debug(f"{process} exited with {code}")
                return code
            except subprocess.TimeoutExpired:
                process.kill()
                logging.error(f"{process} was killed.")

    def prepare(self, tap: PluginInvoker, target: PluginInvoker):
        tap.prepare()
        target.prepare()

    async def invoke(self, tap: PluginInvoker, target: PluginInvoker):
        try:
            # use standard pipes here because we
            # don't need async processing between the
            # tap and target.
            target_in, tap_out = os.pipe()

            p_target, p_tap = None, None
            p_target = await target.invoke_async(
                stdin=target_in, stdout=asyncio.subprocess.PIPE  # state log
            )
            os.close(target_in)

            p_tap = await tap.invoke_async(stdout=tap_out)
            os.close(tap_out)
        except Exception as err:
            if p_tap:
                p_tap.kill()
            if p_target:
                p_target.kill()
            raise Exception(f"Cannot start tap or target: {err}")

        # receive the target stdout and update the current job
        # for each lines
        await asyncio.wait(
            [self.bookmark(p_target.stdout), p_target.wait(), p_tap.wait()],
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
        # the `state.json` is stored in the database
        finder = JobFinder(self.job_id)
        state_job = finder.latest_with_payload(session, flags=SingerPayload.STATE)

        if state_job and "singer_state" in state_job.payload:
            logging.info(f"Found state from {state_job.started_at}.")
            with tap.files["state"].open("w+") as state:
                json.dump(state_job.payload["singer_state"], state)
        else:
            logging.warning("No state was found, complete import.")

    def bookmark_state(self, new_state: str):
        try:
            new_state = json.loads(new_state)

            self.job.payload["singer_state"] = new_state.get("value", {})
            self.job.payload_flags |= SingerPayload.STATE
            self.job.ended_at = datetime.utcnow()
            logging.info(f"Incremental state has been updated at {self.job.ended_at}.")
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

    def dry_run(self, extractor: SingerTap, loader: SingerTarget):
        tap_exec = extractor.exec_path()
        target_exec = loader.exec_path()

        logging.info("Dry run:")
        logging.info(f"\textractor: {extractor.name} at '{tap_exec}'")
        logging.info(f"\tloader: {extractor.name} at '{target_exec}'")

    def run(self, extractor: str, loader: str, dry_run=False):
        tap = self.config_service.get_plugin(PluginType.EXTRACTORS, extractor)
        target = self.config_service.get_plugin(PluginType.LOADERS, loader)

        extractor = PluginInvoker(self.project, tap)
        loader = PluginInvoker(self.project, target)
        self.prepare(extractor, loader)

        if dry_run:
            return self.dry_run(tap, target)

        try:
            session = self._session_cls()
            with self.job.run(session):
                self.restore_bookmark(session, extractor)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.invoke(extractor, loader))
        finally:
            session.close()
