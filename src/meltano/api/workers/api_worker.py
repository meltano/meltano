"""Starts WSGI Webserver that will run the API App for a Meltano Project."""
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
        """Run the initalized API Workers with the App Server requested."""
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
        ]

        # Start uvicorn using the MeltanoInvoker
        if self.reload:

            args += [
                "--reload",
            ]

        # Add the Meltano API app, factory create_app function combo to the args
        args += [
            "--factory",
            "meltano.api.app:create_app",
        ]

        MeltanoInvoker(self.project).invoke(args, command="uvicorn")

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
