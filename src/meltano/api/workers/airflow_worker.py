import logging
import threading
import time
import psutil

from meltano.core.project import Project
from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.config_service import ConfigService, PluginMissingError
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.db import project_engine
from meltano.core.utils.pidfile import PIDFile, UnknownProcessError


class AirflowWorker(threading.Thread):
    def __init__(self, project: Project):
        super().__init__(name="AirflowWorker")

        self.project = project
        self.config_service = ConfigService(project)
        self.add_service = ProjectAddService(
            project, config_service=self.config_service
        )
        self.install_service = PluginInstallService(
            project, config_service=self.config_service
        )
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
