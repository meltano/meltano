import datetime
import subprocess
import logging
import os

from flask_executor import Executor

from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project

executor_elt = Executor()


def setup_executor(app, project):
    executor_elt.init_app(app)


def run_elt(project: Project, schedule_payload: dict):
    job_id = schedule_payload["name"]
    extractor = schedule_payload["extractor"]
    loader = schedule_payload["loader"]
    transform = schedule_payload.get("transform")

    cmd = [
        "meltano",
        "elt",
        "--job_id",
        job_id,
        extractor,
        loader,
        "--transform",
        transform,
    ]
    executor_elt.submit(
        subprocess.run, cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    logging.debug(f"Defered `{' '.join(cmd)}` to the executor.")

    return job_id
