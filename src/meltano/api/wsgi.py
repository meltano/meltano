import os
from meltano.core.project import Project
from meltano.core.db import project_engine
# from meltano.api.workers import MeltanoBackgroundCompiler, AirflowWorker

bind = ["0.0.0.0:5000"]
_project = Project.find()
#pidfile = ".meltano/run/gunicorn.pid"
workers = 4
timeout = 600


def when_ready(arbiter):
    project_engine(_project, os.getenv("MELTANO_DATABASE_URI"), default=True)
