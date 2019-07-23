import datetime
import subprocess
import logging
import os

from flask_executor import Executor

from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project

executor = Executor()  # TODO name this executor_elt, follow the security pattern


def setup_executor(app, project):
    executor.init_app(app)


def run_elt(project: Project, schedule_payload: dict):
    job_id = f'job_{schedule_payload.get("name")}'
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
    executor.submit(subprocess.run, cmd, capture_output=True)
    logging.debug(f"Defered `{' '.join(cmd)}` to the executor.")

    return job_id
