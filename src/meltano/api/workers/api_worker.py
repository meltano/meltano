"""Starts WSGI Webserver that will run the API App for a Meltano Project."""
from __future__ import annotations

import logging
import platform
import threading

from meltano.core.meltano_invoker import MeltanoInvoker
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.settings_service import FeatureFlags
from meltano.core.utils.pidfile import PIDFile


class APIWorker(threading.Thread):
    """The Base APIWorker Class."""

    def __init__(self, project: Project, reload=False):
        """Initialize the API Worker class with the project config.

        Args:
            project: Project class.
            reload: Boolean.
        """
        super().__init__()

        self.project = project
        self.reload = reload
        self.pid_file = PIDFile(self.project.run_dir("gunicorn.pid"))
        self.settings_service = ProjectSettingsService(self.project.find())

    def run(self):
        """Run the initalized API Workers with the App Server requested."""
        with self.settings_service.feature_flag(
            FeatureFlags.ENABLE_UVICORN, raise_error=False
        ) as allow:

            enable_uvicorn = allow

            # Use Uvicorn when on Windows
            if platform.system() == "Windows":
                if enable_uvicorn:
                    logging.debug("ff.enable_uvicorn enabled, starting uvicorn.")
                else:
                    logging.warning(
                        "Windows OS detected auto setting ff.enable_uvicorn"
                    )
                    logging.warning(
                        "Add ff.enable_uvicorn: True to your meltano.yml to supress this waring"
                    )
                    enable_uvicorn = True

            # Start uvicorn to serve API and Ui
            if enable_uvicorn:
                settings_for_apiworker = self.settings_service

                arg_bind_host = str(settings_for_apiworker.get("ui.bind_host"))
                arg_bind_port = str(settings_for_apiworker.get("ui.bind_port"))
                arg_loglevel = str(settings_for_apiworker.get("cli.log_level"))
                arg_forwarded_allow_ips = str(
                    settings_for_apiworker.get("ui.forwarded_allow_ips")
                )

                # If windows and 127.0.0.1 only allowed changing bind host to accomidate
                if platform.system() == "Windows":
                    if (
                        arg_forwarded_allow_ips == "127.0.0.1"
                        and arg_bind_host == "0.0.0.0"  # noqa: S104
                    ):
                        # If left at 0.0.0.0 the server will respond to any request receieved on any interface
                        arg_bind_host = "127.0.0.1"

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
                    "--forwarded-allow-ips",
                    arg_forwarded_allow_ips,
                    "--timeout-keep-alive",
                    "600",
                ]

                # Add reload argument if reload is true
                if self.reload:

                    args += [
                        "--reload",
                    ]

                # Add the Meltano API app, factory create_app function combo to the args
                args += [
                    "--factory",
                    "meltano.api.app:create_app",
                ]

                # Start uvicorn using the MeltanoInvoker
                MeltanoInvoker(self.project).invoke(args, command="uvicorn")

            else:
                # Use Gunicorn when feature flag start_uvicorn is not set

                args = [
                    "--config",
                    "python:meltano.api.wsgi",
                    "--pid",
                    str(self.pid_file),
                ]

                if self.reload:
                    args += ["--reload"]

                args += ["meltano.api.app:create_app()"]

                MeltanoInvoker(self.project).invoke(args, command="gunicorn")

    def pid_path(self):
        """Give the path name of the projects gunicorn.pid file location.

        Returns:
            Path object that gives the direct locationo of the gunicorn.pid file.
        """
        return self.project.run_dir("gunicorn.pid")

    def stop(self):
        """Terminnate active gunicorn workers that have placed a PID in the project's gunicorn.pid file."""
        self.pid_file.process.terminate()
