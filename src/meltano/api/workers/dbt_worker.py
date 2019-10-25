import logging
import threading
import subprocess
import asyncio

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED
from meltano.core.project import Project
from meltano.core.dbt_service import DbtService


class DbtEventHandler(PatternMatchingEventHandler):
    def __init__(self, queue):
        super().__init__()

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
    def __init__(self, project: Project, dbt_service: DbtService = None):
        super().__init__()
        self.project = project
        self.dbt_service = dbt_service or DbtService(project)
        self.observer = None
        self._loop = None

    @property
    def transform_dir(self):
        return self.project.root_dir("transform")

    def setup_observer(self, queue):
        # write every FS events in the Queue
        event_handler = DbtEventHandler(queue)

        observer = Observer()
        observer.schedule(
            event_handler, str(self.transform_dir.joinpath("models")), recursive=True
        )
        observer.schedule(
            event_handler,
            str(self.transform_dir.joinpath("dbt_modules")),
            recursive=True,
        )

        return observer

    async def process(self):
        while True:
            logging.info("Awaiting task")

            await self._queue.get()
            self._queue.task_done()

            # wait for debounce
            await asyncio.sleep(5)

            # drain the queue
            while not self._queue.empty():
                self._queue.get_nowait()
                self._queue.task_done()

            # trigger the task
            await self.dbt_service.docs("generate")

    def start(self):
        try:
            self._loop = asyncio.get_event_loop()
            self._queue = asyncio.Queue(maxsize=1, loop=self._loop)

            # we need to prime the ChildWatcher here so we can
            # call subprocesses asynchronously from threads
            #
            # see https://docs.python.org/3/library/asyncio-subprocess.html#subprocess-and-threads
            # TODO: remove when running on Python 3.8
            asyncio.get_child_watcher()

            self.observer = self.setup_observer(self._queue)
            self.observer.start()

            super().start()
        except OSError:
            # most probably INotify being full
            logging.warn(f"DbtWorker failed: INotify limit reached.")

    def run(self):
        logging.info(f"Auto-generating dbt docs for in '{self.transform_dir}'")
        self._loop.run_until_complete(self.process())

    def stop(self):
        self.observer.stop()
        self._loop.close()
