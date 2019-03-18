import logging
import threading
import time
import requests
from colorama import Fore

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED

from meltano.core.project import Project
from meltano.core.compiler.project_compiler import ProjectCompiler


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, compiler):
        self.compiler = compiler

        super().__init__(ignore_patterns=["*.m5oc"])

    def on_any_event(self, event):
        self.compiler.compile()


class MeltanoBackgroundCompiler:
    def __init__(self, project: Project, compiler: ProjectCompiler = None):
        self.project = project
        self.compiler = compiler or ProjectCompiler(project)
        self.observer = self.setup_observer()

    def setup_observer(self):
        event_handler = CompileEventHandler(self.compiler)
        observer = Observer()
        observer.schedule(event_handler, str(self.compiler.source_dir), recursive=True)

        return observer

    def start(self):
        self.observer.start()
        logging.info(f"Auto-compiling models in {self.observer}.")

    def stop(self):
        self.observer.stop()


class UIAvailableWorker(threading.Thread):
    def __init__(self, url):
        super().__init__()

        self._terminate = False
        self.url = url

    def run(self):
        while not self._terminate:
            try:
                response = requests.get(self.url)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}Meltano is available at {self.url}{Fore.RESET}")
                    self._terminate = True
            except:
                pass

            time.sleep(2)

    def stop(self):
        self._terminate = True
