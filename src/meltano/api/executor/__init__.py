from __future__ import annotations

import logging
import subprocess

from flask_executor import Executor

from meltano.api.models import db
from meltano.api.signals import PipelineSignals
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project
from meltano.core.schedule_service import ScheduleService

executor = Executor()
logger = logging.getLogger(__name__)


def setup_executor(app, project):
    executor.init_app(app)


def defer_run_schedule(name):
    project = Project.find()
    schedule_service = ScheduleService(project)

    schedule = schedule_service.find_schedule(name)
    result = schedule_service.run(
        schedule,
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
    PipelineSignals.on_complete(schedule, success=result.returncode == 0)


def run_schedule(project: Project, name):
    executor.submit(defer_run_schedule, name)
    logger.debug(f"Defered `run_schedule` to the executor with {name}.")

    return name


def defer_upgrade():
    project = Project.find()

    MeltanoInvoker(project).invoke(
        ["upgrade"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def upgrade():
    executor.submit(defer_upgrade)
