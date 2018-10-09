import os
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path

import click
from . import Runner
from meltano.support.job import Job, JobFinder

VENVS_DIR = Path(os.getenv("SINGER_VENVS_DIR", "/venvs"))
RUN_DIR = Path(os.getenv("SINGER_RUN_DIR"))
TAP_CONFIG_DIR = Path(os.getenv("SINGER_TAP_CONFIG_DIR", "/etc/singer/tap"))
TARGET_CONFIG_DIR = Path(os.getenv("SINGER_TARGET_CONFIG_DIR", "/etc/singer/target"))


def envsubst(src: Path, dst: Path):
    with src.open() as i, \
         dst.open("w+") as o:
        subprocess.Popen(["envsubst"], stdin=i, stdout=o)


def file_has_data(file: Path):
    return file.exists() and file.stat().st_size > 0


class SingerRunner(Runner):
    tap_files = {
        'config': RUN_DIR.joinpath("tap.config.json"),
        'catalog': RUN_DIR.joinpath("tap.properties.json"),
        'state': RUN_DIR.joinpath("state.json"),
    }

    target_files = {
        'config': RUN_DIR.joinpath("target.config.json"),
        'state': RUN_DIR.joinpath("new_state.json"),
    }

    def __init__(self, job_id, **config):
        self.job_id = job_id
        self.tap_output_path = config.get("tap_output_path")

    def exec_path(self, name) -> Path:
        return VENVS_DIR.joinpath(name, "bin", name)

    def prepare(self, tap: str, target: str):
        # the `state.json` is stored in the database
        finder = JobFinder(self.job_id)
        state_job = finder.latest_success()

        if state_job:
            logging.info(f"Found state from {state_job.started_at}.")
            with self.tap_files['state'].open("w+") as state:
                json.dump(state_job.payload['singer_state'], state)
        else:
            logging.warn("No state was found, complete import.")

        config_files = {
            self.tap_files['config']: TAP_CONFIG_DIR.joinpath(f"{tap}.config.json"),
            self.tap_files['catalog']: TAP_CONFIG_DIR.joinpath(f"{tap}.properties.json"),
            self.target_files['config']: TARGET_CONFIG_DIR.joinpath(f"{target}.config.json"),
        }

        for dst, src in config_files.items():
            envsubst(src, dst)

    def invoke(self, tap: str, target: str):
        tap_args = [
            self.exec_path(tap),
            "-c", self.tap_files['config'],
            "--catalog", self.tap_files['catalog'],
        ]

        if file_has_data(self.tap_files['state']):
            tap_args += ["--state", self.tap_files['state']]

        tee_args = [
            "tee",
        ]

        if self.tap_output_path:
            tee_args += [self.tap_output_path]

        target_args = [
            self.exec_path(target),
            "-c", self.target_files['config'],
        ]

        try:
            p_target, p_tee, p_tap = None, None, None
            p_target = subprocess.Popen(map(str, target_args),
                                        stdin=subprocess.PIPE,
                                        stdout=self.target_files['state'].open("w+"))

            p_tee = subprocess.Popen(map(str, tee_args),
                                    stdin=subprocess.PIPE,
                                    stdout=p_target.stdin)

            p_tap = subprocess.Popen(map(str, tap_args),
                                    stdout=p_tee.stdin)
        except Exception as err:
            for p in (p_target, p_tee, p_tap):
                if p: p.kill()
            raise Exception(f"Cannot start tap or target: {err}")

        tap_code = p_tap.wait()

        if tap_code != 0:
            p_tee.kill()
            p_target.kill()
            raise Exception(f"Tap exited with {tap_code}")

        target_code = p_target.wait()

        if target_code != 0:
            raise Exception(f"Target exited with {target_code}")

    def bookmark(self):
        state_file = self.target_files['state']
        if not file_has_data(state_file):
            raise Exception(f"Invalid state file: {state_file} is empty.")

        with state_file.open() as state:
            self.job.payload['singer_state'] = json.load(state)

    def run(self, extractor_name: str, loader_name: str):
        self.job = Job(elt_uri=self.job_id)

        with self.job.run():
            self.prepare(extractor_name, loader_name)
            self.invoke(extractor_name, loader_name)
            self.bookmark()
