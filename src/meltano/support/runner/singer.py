import os
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path

import click
from . import Runner
from meltano.support.job import Job, JobFinder


def envsubst(src: Path, dst: Path):
    with src.open() as i, dst.open("w+") as o:
        subprocess.Popen(["envsubst"], stdin=i, stdout=o)


def file_has_data(file: Path):
    return file.exists() and file.stat().st_size > 0


class SingerRunner(Runner):
    def __init__(self, job_id, **config):
        self.job_id = job_id
        self.job = Job(elt_uri=self.job_id)

        self.run_dir = Path(config.get("run_dir", os.getenv("SINGER_RUN_DIR")))
        self.venvs_dir = Path(
            config.get("venvs_dir", os.getenv("SINGER_VENVS_DIR", "/venvs"))
        )
        self.tap_config_dir = Path(
            config.get(
                "tap_config_dir", os.getenv("SINGER_TAP_CONFIG_DIR", "/etc/singer/tap")
            )
        )
        self.target_config_dir = Path(
            config.get(
                "target_config_dir",
                os.getenv("SINGER_TARGET_CONFIG_DIR", "/etc/singer/target"),
            )
        )
        self.tap_output_path = config.get("tap_output_path")

        self.tap_files = {
            "config": self.run_dir.joinpath("tap.config.json"),
            "catalog": self.run_dir.joinpath("tap.properties.json"),
            "state": self.run_dir.joinpath("state.json"),
        }
        self.target_files = {
            "config": self.run_dir.joinpath("target.config.json"),
            "state": self.run_dir.joinpath("new_state.json"),
        }

    def exec_path(self, name) -> Path:
        return self.venvs_dir.joinpath(name, "bin", name)

    def prepare(self, tap: str, target: str):
        # the `state.json` is stored in the database
        finder = JobFinder(self.job_id)
        state_job = finder.latest_success()

        if state_job:
            logging.info(f"Found state from {state_job.started_at}.")
            with self.tap_files["state"].open("w+") as state:
                json.dump(state_job.payload["singer_state"], state)
        else:
            logging.warn("No state was found, complete import.")

        config_files = {
            self.tap_files["config"]: self.tap_config_dir.joinpath(
                f"{tap}.config.json"
            ),
            self.tap_files["catalog"]: self.tap_config_dir.joinpath(
                f"{tap}.properties.json"
            ),
            self.target_files["config"]: self.target_config_dir.joinpath(
                f"{target}.config.json"
            ),
        }

        for dst, src in config_files.items():
            envsubst(src, dst)

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

    def invoke(self, tap: str, target: str):
        tap_args = [
            self.exec_path(tap),
            "-c",
            self.tap_files["config"],
            "--catalog",
            self.tap_files["catalog"],
        ]

        if file_has_data(self.tap_files["state"]):
            tap_args += ["--state", self.tap_files["state"]]

        tee_args = ["tee"]

        if self.tap_output_path:
            tee_args += [self.tap_output_path]

        target_args = [self.exec_path(target), "-c", self.target_files["config"]]

        try:
            p_target, p_tee, p_tap = None, None, None
            p_target = subprocess.Popen(
                map(str, target_args),
                stdin=subprocess.PIPE,
                stdout=self.target_files["state"].open("w+"),
            )

            p_tee = subprocess.Popen(
                map(str, tee_args), stdin=subprocess.PIPE, stdout=p_target.stdin
            )

            p_tap = subprocess.Popen(map(str, tap_args), stdout=p_tee.stdin)
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

    def bookmark(self):
        state_file = self.target_files["state"]
        if not file_has_data(state_file):
            raise Exception(f"Invalid state file: {state_file} is empty.")

        with state_file.open() as state:
            # as per the Singer specification, only the _last_ state
            # should be persisted
            *_, last_state = state.readlines()
            self.job.payload["singer_state"] = json.loads(last_state)

    def run(self, extractor_name: str, loader_name: str):
        with self.job.run():
            self.prepare(extractor_name, loader_name)
            self.invoke(extractor_name, loader_name)
            self.bookmark()
