import os
import logging
import threading
import subprocess
import asyncio

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.config_service import ConfigService, PluginMissingError
from meltano.core.plugin import PluginInstall, PluginType
from meltano.core.dbt_service import DbtService
from meltano.core.db import project_engine


class DbtEventHandler(PatternMatchingEventHandler):
    def __init__(self, queue):
        super().__init__(ignore_patterns=["*.log"])

        self._queue = queue

    def on_any_event(self, event):
        try:
            self._queue.put_nowait(event)
            self._queue._loop._write_to_self()

            logging.debug(f"Put {event} in the queue.")
        except asyncio.QueueFull:
            logging.debug(f"Discard {event} in the queue.")
        except Exception as e:
            logging.error(f"DbtWorker failed: {str(e)}")


class DbtWorker(threading.Thread):
    def __init__(self, project: Project, loader: str, loop=None):
        super().__init__()
        self.project = project
        self.loader = loader
        self.config_service = ConfigService(project)
        self.add_service = ProjectAddService(
            project, config_service=self.config_service
        )
        self.install_service = PluginInstallService(
            project, config_service=self.config_service
        )
        self.observer = None
        self._plugin = None
        self._loop = loop or asyncio.get_event_loop()

    @property
    def transform_dir(self):
        return self.project.root_dir("transform")

    def setup_observer(self, queue):
        # write every FS events in the Queue
        event_handler = DbtEventHandler(queue)

        observer = Observer()
        observer.schedule(event_handler, str(self.transform_dir), recursive=True)

        return observer

    async def process(self, session):
        dbt_service = DbtService(self.project)

        while True:
            # drain the queue
            while not self._queue.empty():
                self._queue.get_nowait()
                self._queue.task_done()

            # trigger the task
            try:
                loader = self.config_service.find_plugin(self.loader)
                await dbt_service.docs(session, loader, "generate")
            except PluginMissingError as err:
                logging.warning(
                    f"Could not generate dbt docs: '{str(err)}' is missing."
                )
            except:
                pass

            # wait for the next trigger
            logging.info("Awaiting task")
            await self._queue.get()
            self._queue.task_done()

            # wait for debounce
            await asyncio.sleep(5)

    def start(self):
        try:
            self._queue = asyncio.Queue(maxsize=1, loop=self._loop)

            self.observer = self.setup_observer(self._queue)
            self.observer.start()

            super().start()
        except OSError as err:
            # most probably INotify being full
            logging.warning(f"DbtWorker failed: INotify limit reached: {err}")

    def run(self):
        try:
            self._plugin = self.config_service.find_plugin("dbt")
        except PluginMissingError as err:
            self._plugin = self.add_service.add(PluginType.TRANSFORMERS, "dbt")
            self.install_service.install_plugin(self._plugin)

        _, Session = project_engine(self.project)

        try:
            session = Session()

            # TODO: this blocks the loop, we should probaly return a `Task` instance from
            # this function and let the caller schedule it on the loop
            # This class would not have to be a Thread an thus it could simplify the
            # handling of such cases in the future
            logging.info(
                f"Auto-generating dbt docs for in '{self.transform_dir}' for {self.loader}"
            )
            self._loop.run_until_complete(self.process(session))
        finally:
            session.close()

    def stop(self):
        if self.observer:
            self.observer.stop()
