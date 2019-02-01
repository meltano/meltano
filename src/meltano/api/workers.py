import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, EVENT_TYPE_MODIFIED

from meltano.core.project import Project
from meltano.api.controllers.m5o_file_parser import MeltanoAnalysisFileParser


class CompileEventHandler(PatternMatchingEventHandler):
    def __init__(self, root_path):
        super().__init__(ignore_patterns=["*.m5oc"])
        self.root_path = root_path

    def on_any_event(self, event):
        try:
            m5o_parse = MeltanoAnalysisFileParser(self.root_path)
            models = m5o_parse.parse()
            m5o_parse.compile(models)
            logging.info(f"Models have been compiled (via {event})")
        except Exception:
            logging.warn(f"Failed to compile models (via {event})")


class MeltanoBackgroundCompiler:
    def __init__(self, project: Project):
        self.project = project
        self.observer = self.setup_observer(project.root.joinpath("model"))

    def setup_observer(self, path):
        event_handler = CompileEventHandler(path)
        observer = Observer()
        observer.schedule(event_handler, str(event_handler.root_path), recursive=True)

        return observer

    def start(self):
        self.observer.start()
        logging.info(f"Auto-compiling models in {self.observer}.")

    def stop(self):
        self.observer.stop()
