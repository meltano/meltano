import os
import subprocess
import threading

from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.project import Project
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    def __init__(self, project: Project, reload=False):
        # print("Hello from api_worker.py at line 12: def __init__(self, project: Project, reload=False):")
        super().__init__()

        self.project = project
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))

    def run(self):
        if os.name == "nt":
            # Use Waitress when on Windows

            args = [
                "--port=5000",
                "--threads=1",
                "--call",
                "meltano.api.app:create_app",
            ]

            MeltanoInvoker(self.project).invoke(args, command="waitress-serve")

        else:
            # print("Hello from api_worker.py: I am not a windows machine lets user Gunicorn")

            args = ["--config", "python:meltano.api.wsgi", "--pid", str(self.pid_file)]

            if self.reload:
                args += ["--reload"]

            args += ["meltano.api.app:create_app()"]

            MeltanoInvoker(self.project).invoke(args, command="gunicorn")

    def pid_path(self):
        return self.project.run_dir(f"gunicorn.pid")

    def stop(self):
        self.pid_file.process.terminate()
