"""Starts WSGI Webserver that will run the API App for a Meltano Project."""
import os
import threading

from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.project import Project
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    """The Base APIWorker Class."""

    def __init__(self, project: Project, reload=False):
        """Initializes the API Worker class with the project config."""
        super().__init__()

        self.project = project
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))

    def run(self):
        """Starts the initalized API Workers with the WSGI Server needed for the detected OS."""
        if os.name == "nt":
            # Use Waitress when on Windows

            args = [
                "--port=5000",
                "--call",
                "meltano.api.app:create_app",
            ]

            MeltanoInvoker(self.project).invoke(args, command="waitress-serve")

        else:
            # Use Gunicorn when not on Windows

            args = ["--config", "python:meltano.api.wsgi", "--pid", str(self.pid_file)]

            if self.reload:
                args += ["--reload"]

            args += ["meltano.api.app:create_app()"]

            MeltanoInvoker(self.project).invoke(args, command="gunicorn")

    def pid_path(self):
        """Returns the path name of the gunicorn.pid file."""
        return self.project.run_dir("gunicorn.pid")

    def stop(self):
        """Terminnate active gunicorn workers that have placed a PID in the project's gunicorn.pid file."""
        self.pid_file.process.terminate()
