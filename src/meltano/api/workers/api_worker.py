"""Starts WSGI Webserver that will run the API App for a Meltano Project."""
import logging
import platform
import threading

from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    """The Base APIWorker Class."""

    def __init__(self, project: Project, reload=False):
        """
        Initialize the API Worker class with the project config.

        Parameters:
            project: Project class.
            reload: Boolean.
        """
        super().__init__()

        self.project = project
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))

    def run(self):
        """Run the initalized API Workers with the WSGI Server needed for the detected OS."""
        if platform.system() == "Windows":
            # Use Uvicorn when on Windows
            settings_for_apiworker = ProjectSettingsService(self.project.find())

            arg_bind_host = str(settings_for_apiworker.get("ui.bind_host"))
            arg_bind_port = str(settings_for_apiworker.get("ui.bind_port"))
            arg_loglevel = str(settings_for_apiworker.get("cli.log_level"))

            # Setup args for uvicorn using bind info from the project setings service
            args = [
                "--host",
                arg_bind_host,
                "--port",
                arg_bind_port,
                "--loop",
                "asyncio",
                "--interface",
                "wsgi",
                "--log-level",
                arg_loglevel,
                "--factory",
                "meltano.api.app:create_app",
            ]

            # Start uvicorn using the MeltanoInvoker
            if self.reload:
                logging.warning(
                    "--reload is not available, you will need to manually stop and start Meltano UI"
                )
            else:
                MeltanoInvoker(self.project).invoke(args, command="uvicorn")

        else:
            # Use Gunicorn when not on Windows
            args = ["--config", "python:meltano.api.wsgi", "--pid", str(self.pid_file)]

            if self.reload:
                args += ["--reload"]

            args += ["meltano.api.app:create_app()"]

            MeltanoInvoker(self.project).invoke(args, command="gunicorn")

    def pid_path(self):
        """
        Give the path name of the projects gunicorn.pid file location.

        Returns:
            Path object that gives the direct locationo of the gunicorn.pid file.
        """
        return self.project.run_dir("gunicorn.pid")

    def stop(self):
        """Terminnate active gunicorn workers that have placed a PID in the project's gunicorn.pid file."""
        self.pid_file.process.terminate()
