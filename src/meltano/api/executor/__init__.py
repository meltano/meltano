import datetime
import subprocess
import logging
import os
from functools import partial
from flask_executor import Executor

from meltano.api.signals import PipelineSignals
from meltano.api.models import db
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project
from meltano.core.meltano_invoker import MeltanoInvoker


executor = Executor()
logger = logging.getLogger(__name__)


def setup_executor(app, project):
    executor.init_app(app)


def defer_run_elt(schedule_payload: dict):
    project = Project.find()

    job_id = schedule_payload["name"]
    extractor = schedule_payload["extractor"]
    loader = schedule_payload["loader"]
    transform = schedule_payload.get("transform")

    args = ["elt", "--job_id", job_id, extractor, loader, "--transform", transform]

    result = MeltanoInvoker(project).invoke(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={"MELTANO_JOB_TRIGGER": "ui"},
    )

    # It would probably be better that we would use sqlalchemy ORM events
    # on the `Job` instance, but it would require more changes as it is
    # a `meltano.core` model.
    #
    # The benefit is that we are currently in an executor Thread, so we can
    # safely send emails without thinking about blocking any requests.
    #
    # The caveat here is that pipeline that runs from Airflow won't trigger
    # this signal, and thus won't send any notification.
    PipelineSignals.on_complete(schedule_payload, success=result.returncode == 0)


def run_elt(project: Project, schedule_payload: dict):
    job_id = schedule_payload["name"]
    executor.submit(defer_run_elt, schedule_payload)
    logger.debug(f"Defered `run_elt` to the executor with {schedule_payload}.")

    return job_id


def defer_upgrade():
    project = Project.find()

    MeltanoInvoker(project).invoke(
        ["upgrade"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def upgrade():
    executor.submit(defer_upgrade)
