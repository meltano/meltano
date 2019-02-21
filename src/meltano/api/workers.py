import logging
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
