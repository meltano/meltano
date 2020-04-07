import logging
import threading
import time
import psutil

from meltano.core.project import Project
from meltano.core.plugin import PluginInstall
from meltano.core.config_service import ConfigService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.db import project_engine
from meltano.core.utils.pidfile import PIDFile, UnknownProcessError


class AirflowWorker(threading.Thread):
    def __init__(self, project: Project):
        super().__init__(name="AirflowWorker")

        self.project = project
        self.config_service = ConfigService(project)
        self._plugin = None
        self.pid_file = PIDFile(self.project.run_dir("airflow", "scheduler.pid"))

    def kill_stale_workers(self):
        process = None
        try:
            process = self.pid_file.process
        except UnknownProcessError:
            pass

        if process is not None:
            logging.debug(
                f"Process {process} is running, possibly stale, terminating it."
            )
            process.terminate()

            def on_terminate(process):
                logging.info(
                    f"Process {process} ended with exit code {process.returncode}"
                )

            _gone, alive = psutil.wait_procs(
                [process], timeout=5, callback=on_terminate
            )

            # kill the rest
            for process in alive:
                process.kill()

        try:
            self.pid_file.unlink()
        except:
            pass

    def start_all(self):
        _, Session = project_engine(self.project)
        logs_path = self.project.run_dir("airflow", "logs", "scheduler.log")

        try:
            session = Session()
            invoker = invoker_factory(
                self.project, self._plugin, prepare_with_session=session
            )

            with logs_path.open("w") as logs_file:
                scheduler = invoker.invoke(
                    "scheduler", "--pid", str(self.pid_file), stdout=logs_file
                )
                self.pid_file.write_pid(scheduler.pid)
        finally:
            session.close()

    def run(self):
        self._plugin = self.config_service.find_plugin("airflow")

        self.kill_stale_workers()
        self.start_all()

    def stop(self):
        self.kill_stale_workers()
