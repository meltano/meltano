import os
import threading
import subprocess

from meltano.core.project import Project
from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    def __init__(self, project: Project, reload=False):
        super().__init__()

        self.project = project
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))

    def run(self):
        args = ["--config", "python:meltano.api.wsgi", "--pid", str(self.pid_file)]

        if self.reload:
            args += ["--reload"]

        args += ["meltano.api.app:create_app()"]

        MeltanoInvoker(self.project).invoke(args, command="gunicorn")

    def pid_path(self):
        return self.project.run_dir(f"gunicorn.pid")

    def stop(self):
        self.pid_file.process.terminate()
