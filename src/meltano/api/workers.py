import logging
import requests
import threading
import time
import webbrowser
import psutil
from colorama import Fore

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED
from meltano.core.project import Project
from meltano.core.plugin import PluginInstall
from meltano.core.config_service import ConfigService
from meltano.core.compiler.project_compiler import ProjectCompiler
from meltano.core.plugin_invoker import invoker_factory
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


class AirflowWorker(threading.Thread):
    def __init__(self, project: Project, airflow: PluginInstall = None):
        super().__init__()

        self.project = project
        self._plugin = airflow or ConfigService(project).find_plugin("airflow")
        self._webserver = None
        self._scheduler = None

    def kill_stale_workers(self):
        stale_workers = []
        workers_pid = map(self.pid_path, ("webserver", "scheduler"))

        for f in workers_pid:
            try:
                pid = int(f.open().read())
                stale_workers.append(psutil.Process(pid))
            except psutil.NoSuchProcess:
                f.unlink()
            except FileNotFoundError:
                pass

        def on_terminate(proc):
            logging.info(f"Process {proc} ended with exit code {proc.returncode}")

        for p in stale_workers:
            logging.debug(f"Process {p} is stale, terminating it.")
            p.terminate()

        gone, alive = psutil.wait_procs(stale_workers, timeout=5, callback=on_terminate)

        # kill the rest
        for p in alive:
            p.kill()

    def start_all(self):
        logs_dir = self.project.run_dir("airflow", "logs")
        invoker = invoker_factory(db.session, self.project, self._plugin)

        with logs_dir.joinpath("webserver.log").open(
            "w"
        ) as webserver, logs_dir.joinpath("scheduler.log").open(
            "w"
        ) as scheduler, self.pid_path(
            "webserver"
        ).open(
            "w"
        ) as webserver_pid, self.pid_path(
            "scheduler"
        ).open(
            "w"
        ) as scheduler_pid:
            self._webserver = invoker.invoke("webserver", "-w", "1", stdout=webserver)
            self._scheduler = invoker.invoke("scheduler", stdout=scheduler)

            webserver_pid.write(str(self._webserver.pid))
            scheduler_pid.write(str(self._scheduler.pid))

    def pid_path(self, name):
        return self.project.run_dir("airflow", f"{name}.pid")

    def run(self):
        self.kill_stale_workers()
        self.start_all()

    def stop(self):
        self.kill_stale_workers()
