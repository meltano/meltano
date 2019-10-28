import os
import threading
import subprocess

from meltano.core.project import Project
from meltano.core.db import project_engine
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    def __init__(self, project: Project, bind_addr, reload=False):
        super().__init__()
        self.project = project
        self.bind_addr = bind_addr
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))

    def run(self):
        # fmt: off
        cmd = ["gunicorn",
               "--bind", self.bind_addr,
               "--config", "python:meltano.api.wsgi",
               "--pid", str(self.pid_file)]
        # fmt: on

        if self.reload:
            cmd += ["--reload"]

        cmd += ["meltano.api.app:create_app()"]

        engine, _ = project_engine(self.project)
        subprocess.run(cmd, env={**os.environ, "MELTANO_DATABASE_URI": str(engine.url)})

    def pid_path(self):
        return self.project.run_dir(f"gunicorn.pid")

    def stop(self):
        self.pid_file.process.terminate()
