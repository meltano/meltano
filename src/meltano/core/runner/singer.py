import os
import subprocess
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import click
from . import Runner
from meltano.core.job import Job, JobFinder
from meltano.core.venv_service import VenvService
from meltano.core.project import Project
from meltano.core.plugin import PluginType

# from meltano.support.config_service import ConfigService


class ConfigService:
    def __init__(self, project: Project):
        self.project = project

    def database(self, database: str):
        return os.environ.copy()


def envsubst(src: Path, dst: Path, env={}):
    # find viable substitutions
    var_matcher = re.compile('''
      \$                # starts with a '$'
      (?:              # either $VAR or ${VAR}
        {(\w+)}|(\w+)  # capture the variable name as group[0] or group[1]
      )
    ''', re.VERBOSE)

    env_override = os.environ.copy()
    env_override.update(env)

    def subst(match) -> str:
        try:
            # the variable can be in either group
            var = next(var
                       for var in match.groups()
                       if var)
            return str(env_override[var])
        except KeyError as e:
            logging.warning(f"Variable {var} is missing from the environment.")
            return None

    with src.open() as i, dst.open("w+") as o:
        output = re.sub(var_matcher,
                        subst,
                        i.read())
        o.write(output)


def file_has_data(file: Path):
    return file.exists() and file.stat().st_size > 0


class SingerRunner(Runner):
    def __init__(
        self,
        project: Project,
        job_id,
        venv_service: VenvService = None,
        config_service: ConfigService = None,
        **config,
    ):
        self.project = project
        self.job_id = job_id
        self.venv_service = venv_service or VenvService(project)
        self.config_service = config_service or ConfigService(project)
        self.config = config

        self.job = Job(elt_uri=self.job_id)
        self.run_dir = Path(config.get("run_dir", "/run/singer"))
        self.tap_config_dir = Path(config.get("tap_config_dir", "/etc/singer/tap"))
        self.tap_catalog_dir = Path(config.get("tap_catalog_dir", self.tap_config_dir))
        self.target_config_dir = Path(
            config.get("target_config_dir", "/etc/singer/target")
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

    @property
    def database(self):
        return self.config.get("database", "default")

    def exec_path(self, plugin_type, plugin_name) -> Path:
        return self.venv_service.exec_path(plugin_name, namespace=plugin_type)

    def prepare(self, tap: str, target: str):
        os.makedirs(self.project.run_dir(), exist_ok=True)

        config_files = {
            self.tap_files["config"]: self.tap_config_dir.joinpath(
                f"{tap}.config.json"
            ),
            self.tap_files["catalog"]: self.tap_catalog_dir.joinpath(
                f"{tap}.properties.json"
            ),
            self.target_files["config"]: self.target_config_dir.joinpath(
                f"{target}.config.json"
            ),
        }

        for dst, src in config_files.items():
            try:
                envsubst(src, dst, env=self.config_service.database(self.database))
            except FileNotFoundError:
                logging.warn(f"Could not find {src.name} in {src.resolve()}, skipping.")

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
            self.exec_path(PluginType.EXTRACTORS, tap),
            "--config",
            self.tap_files["config"],
        ]

        if file_has_data(self.tap_files["catalog"]):
            tap_args += ["--catalog", self.tap_files["catalog"]]

        if file_has_data(self.tap_files["state"]):
            tap_args += ["--state", self.tap_files["state"]]

        tee_args = ["tee"]

        if self.tap_output_path:
            tee_args += [self.tap_output_path]

        target_args = [
            self.exec_path(PluginType.LOADERS, target),
            "-c",
            self.target_files["config"],
        ]

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

    def restore_bookmark(self):
        # the `state.json` is stored in the database
        finder = JobFinder(self.job_id)
        state_job = finder.latest_success()

        if state_job and "singer_state" in state_job.payload:
            logging.info(f"Found state from {state_job.started_at}.")
            with self.tap_files["state"].open("w+") as state:
                json.dump(state_job.payload["singer_state"], state)
        else:
            logging.warn("No state was found, complete import.")

    def bookmark(self):
        state_file = self.target_files["state"]
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

    def dry_run(self, extractor_name: str, loader_name: str):
        self.prepare(extractor_name, loader_name)
        tap_exec = self.exec_path(PluginType.EXTRACTORS, extractor_name)
        target_exec = self.exec_path(PluginType.LOADERS, loader_name)

        logging.info("Dry run:")
        logging.info(f"\textractor: {extractor_name} at '{tap_exec}'")
        logging.info(f"\tloader: {extractor_name} at '{target_exec}'")

    def run(self, extractor_name: str, loader_name: str, dry_run=False):
        if dry_run:
            return self.dry_run(extractor_name, loader_name)

        with self.job.run():
            self.restore_bookmark()
            self.prepare(extractor_name, loader_name)
            self.invoke(extractor_name, loader_name)
            self.bookmark()
