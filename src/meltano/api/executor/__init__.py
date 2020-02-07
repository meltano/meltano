import datetime
import subprocess
import logging
import os
from functools import partial
from flask_executor import Executor
from flask_mail import Message

from meltano.api.mail import mail
from meltano.core.plugin import PluginRef, PluginType
from meltano.core.project import Project


executor = Executor()


def setup_executor(app, project):
    executor.init_app(app)


def defer_run_elt(schedule_payload: dict):
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

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # send a success email?
    msg = Message(subject="A new Data Source is ready!",
                  body="Congratulations my man!",
                  recipients=["mbergeron@gitlab.com"])

    mail.send(msg)


def run_elt(project: Project, schedule_payload: dict):
    job_id = schedule_payload["name"]
    executor.submit(defer_run_elt, schedule_payload)

    return job_id


def upgrade():
    cmd = ["meltano", "upgrade"]
    executor.submit(
        subprocess.run, cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
