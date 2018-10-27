import os
import subprocess
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

import click
from . import Runner
from meltano.core.job import Job, JobFinder
from meltano.core.venv_service import VenvService
from meltano.core.project import Project
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.plugin import (
    Plugin,
    PluginType,
    PluginMissingError,
)
from meltano.core.plugin.singer import (
    SingerTap,
    SingerTarget
)
from meltano.core.utils import file_has_data


class SingerRunner(Runner):
    def __init__(
        self,
        project: Project,
        job_id,
        **config,
    ):
        self.project = project
        self.job_id = job_id
        self.config = config

        self.job = Job(elt_uri=self.job_id)

        self.run_dir = Path(config.get("run_dir", "/run/singer"))
        self.tap_config_dir = Path(config.get("tap_config_dir", "/etc/singer/tap"))
        self.target_config_dir = Path(config.get("target_config_dir", "/etc/singer/target"))
        self.tap_output = config.get("tap_output", False)

    @property
    def database(self):
        return self.config.get("database", "default")

    def prepare(self, tap: PluginInvoker, target: PluginInvoker):
        tap.prepare()
        target.prepare()

    def stop(self, process, **wait_args):
        if process.stdin:
            process.stdin.close()

        while True:
            try:
                code = process.wait(**wait_args)
                logging.debug(f"{process} exited with {code}")
                return code
            except subprocess.TimeoutExpired:
                process.kill()
                logging.error(f"{process} was killed.")

    def invoke(self, tap: PluginInvoker, target: PluginInvoker):
        tee_args = ["tee"]

        if self.tap_output:
            tee_args += [tap.files["output"]]

        try:
            p_target, p_tee, p_tap = None, None, None
            p_target = target.invoke(
                stdin=subprocess.PIPE,
                stdout=target.files["state"].open("w+"),
            )

            p_tee = subprocess.Popen(
                map(str, tee_args),
                stdin=subprocess.PIPE,
                stdout=p_target.stdin
            )

            p_tap = tap.invoke(stdout=p_tee.stdin)
        except Exception as err:
            for p in (p_target, p_tee, p_tap):
                self.stop(p, timeout=0)
            raise Exception(f"Cannot start tap or target: {err}")

        tap_code = self.stop(p_tap)
        tee_code = self.stop(p_tee)
        target_code = self.stop(p_target)

        if any((tap_code, tee_code, target_code)):
            raise Exception(
                f"Subprocesses didn't exit cleanly: tap({tap_code}), target({target_code}), tee({tee_code})"
            )

    def restore_bookmark(self, tap: SingerTap):
        # the `state.json` is stored in the database
        finder = JobFinder(self.job_id)
        state_job = finder.latest_success()

        if state_job and "singer_state" in state_job.payload:
            logging.info(f"Found state from {state_job.started_at}.")
            with tap.files["state"].open("w+") as state:
                json.dump(state_job.payload["singer_state"], state)
        else:
            logging.warn("No state was found, complete import.")

    def bookmark(self, target: SingerTarget):
        state_file = target.files["state"]
        if not file_has_data(state_file):
            logging.warn(
                "State file is empty, this run will not update the incremental state."
            )
            return

        with state_file.open() as state:
            # as per the Singer specification, only the _last_ state
            # should be persisted
            *_, last_state = state.readlines()
            self.job.payload["singer_state"] = json.loads(last_state)

    def dry_run(self,
                extractor: SingerTap,
                loader: SingerTarget):
        self.prepare(extractor, loader)
        tap_exec = extractor.exec_path()
        target_exec = loader.exec_path()

        logging.info("Dry run:")
        logging.info(f"\textractor: {extractor.name} at '{tap_exec}'")
        logging.info(f"\tloader: {extractor.name} at '{target_exec}'")

    def run(self,
            extractor: str,
            loader: str,
            dry_run=False):
        tap, target = SingerTap(extractor), SingerTarget(loader)
        extractor = PluginInvoker(self.project,
                                  tap)
        loader = PluginInvoker(self.project,
                               target)

        if dry_run:
            return self.dry_run(tap, target)

        with self.job.run():
            self.restore_bookmark(extractor)
            self.prepare(extractor, loader)
            self.invoke(extractor, loader)
            self.bookmark(loader)
