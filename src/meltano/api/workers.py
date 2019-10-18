import os
import logging
import requests
import threading
import time
import webbrowser
import psutil
import subprocess
from colorama import Fore

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED
from meltano.core.project import Project
from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.config_service import ConfigService, PluginMissingError
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.db import project_engine
from meltano.core.utils.pidfile import PIDFile, UnknownProcessError
from meltano.api.models import db


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, compiler):
        self.compiler = compiler

        super().__init__(ignore_patterns=["*.m5oc"])

    def on_any_event(self, event):
        try:
            self.compiler.compile()
        except Exception as e:
            logging.error(f"Compilation failed: {str(e)}")


class MeltanoBackgroundCompiler:
    def __init__(self, project: Project, compiler: ProjectCompiler = None):
        self.project = project
        self.compiler = compiler or ProjectCompiler(project)
        self.observer = self.setup_observer()

    @property
    def model_dir(self):
        return self.project.root_dir("model")

    def setup_observer(self):
        event_handler = CompileEventHandler(self.compiler)
        observer = Observer()
        observer.schedule(event_handler, str(self.model_dir), recursive=True)

        return observer

    def start(self):
        try:
            self.observer.start()
            logging.info(f"Auto-compiling models in '{self.model_dir}'")
        except OSError:
            # most probably INotify being full
            logging.warn(f"Model auto-compilation is disabled: INotify limit reached.")

    def stop(self):
        self.observer.stop()


class UIAvailableWorker(threading.Thread):
    def __init__(self, url, open_browser=False):
        super().__init__()
        self._terminate = False

        self.url = url
        self.open_browser = open_browser

    def run(self):
        while not self._terminate:
            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}Meltano is available at {self.url}{Fore.RESET}")
                    if self.open_browser:
                        webbrowser.open(self.url)
                    self._terminate = True

            except:
                pass

            time.sleep(2)

    def stop(self):
        self._terminate = True


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


class AirflowWorker(threading.Thread):
    def __init__(self, project: Project):
        super().__init__(name="AirflowWorker")

        self.project = project
        self.add_service = ProjectAddService(project)
        self.install_service = PluginInstallService(project)
        self.config_service = ConfigService(project)
        self._plugin = None
        self._webserver = None
        self._scheduler = None

    def kill_stale_workers(self):
        stale_workers = []
        workers_pid_files = map(self.pid_file, ("webserver", "scheduler"))

        for pid_file in workers_pid_files:
            try:
                stale_workers.append(pid_file.process)
            except UnknownProcessError:
                pass

        def on_terminate(process):
            logging.info(f"Process {process} ended with exit code {process.returncode}")

        for process in stale_workers:
            logging.debug(f"Process {process} is stale, terminating it.")
            process.terminate()

        gone, alive = psutil.wait_procs(stale_workers, timeout=5, callback=on_terminate)

        # kill the rest
        for process in alive:
            process.kill()

        for pid_file in workers_pid_files:
            try:
                pid_file.unlink()
            except:
                pass

    def start_all(self):
        _, Session = project_engine(self.project)
        logs_dir = self.project.run_dir("airflow", "logs")

        try:
            session = Session()
            invoker = invoker_factory(
                self.project, self._plugin, prepare_with_session=session
            )

            # fmt: off
            with logs_dir.joinpath("webserver.log").open("w") as webserver, \
              logs_dir.joinpath("scheduler.log").open("w") as scheduler:
                self._webserver = invoker.invoke("webserver", "-w", "1", stdout=webserver)
                self._scheduler = invoker.invoke("scheduler", stdout=scheduler)

                self.pid_file("webserver").write_pid(self._webserver.pid)
                self.pid_file("scheduler").write_pid(self._scheduler.pid)
            # fmt: on

            # Time padding for server initialization so UI iframe displays as expected
            # (iteration potential on approach but following UIAvailableWorker sleep approach)
            time.sleep(2)
        finally:
            session.close()

    def pid_file(self, name) -> PIDFile:
        return PIDFile(self.project.run_dir("airflow", f"{name}.pid"))

    def run(self):
        try:
            self._plugin = self.config_service.find_plugin("airflow")
        except PluginMissingError as err:
            self._plugin = self.add_service.add(PluginType.ORCHESTRATORS, "airflow")
            self.install_service.install_plugin(self._plugin)

        self.kill_stale_workers()
        self.start_all()

    def stop(self):
        self.kill_stale_workers()
